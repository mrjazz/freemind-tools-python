<?php


if (isset($_SERVER['argv']) && count($_SERVER['argv']) > 2) {
    $doc = file_get_contents($_SERVER['argv'][1]);

    $xml = new SimpleXMLElement($doc);
    // print_as_tree($xml);
    if (count($_SERVER['argv']) == 4) {
        $cycles = $_SERVER['argv'][3];
    } else {
        $cycles = 1;
    }
    generate_test_cases($xml, $_SERVER['argv'][2], $cycles);
} else {
    echo "Path to mindmap and root node missed\n";
    exit();
}


function traverse($xml, $fn, $level = 0) {
    $result = $fn($xml, $level);
    if ($result !== false) {
        return $result;
    }

    if ($xml->count() > 0) {
        foreach ($xml->children() as $child) {
            $result = traverse($child, $fn, $level+2);
            if ($result !== false) {
                return $result;
            }
        }
    }

    return false;
}

function print_as_tree($xml) {
    traverse($xml, function ($node, $level) {
        if (trim($node['TEXT']) !== '') {
            echo str_repeat('  ', $level) . $node['TEXT'] . "\n";
        }
        return false;
    });
}

function find_node($xml, $searchNode) {
    return traverse($xml, function ($node, $level) use ($searchNode) {
        if ((new FlowNode($node['TEXT']))->getTitle() === $searchNode) {
            return $node;
        }
        return false;
    });
}

class FlowNode {

    const TYPE_END = 1;
    const TYPE_REF = 2;
    const TYPE_CASE = 3;

    private $nodeTitle;
    private $title;
    private $type;
    private $ref;

    public function __construct($nodeTitle) {
        $this->nodeTitle = $nodeTitle;
        $title = trim(preg_replace('/[\(\[].*$/', '', $nodeTitle));
        $this->title = $title;

        if (strtoupper($title) === 'END') {
            $this->type = self::TYPE_END;
        } elseif (stripos($title, 'GOTO:') === 0) {
            $this->type = self::TYPE_REF;
            $this->ref = trim(substr($title, strlen('GOTO:')));
        } else {
            $this->type = self::TYPE_CASE;
        }
    }

    /**
     * @return mixed
     */
    public function getNodeTitle() {
        return $this->nodeTitle;
    }

    public function getType() {
        return $this->type;
    }

    /**
     * @return string
     */
    public function getTitle() {
        return $this->title;
    }

    /**
     * @return bool|string
     */
    public function getRef() {
        return $this->ref;
    }
}

class TestCaseDetector {

    private $rootXml;

    private $cyclesAllowed = 1;


    const RESULT_OK = 'Ok';
    const RESULT_NOT_TERMINATED = 'NotTerminated';
    const RESULT_CYCLES = 'Cycles';

    private $resultCycles = [];
    private $resultOk = [];
    private $resultNotTerminated = [];

    public function __construct($rootXml, $cyclesAllowed) {
        $this->rootXml = $rootXml;
        $this->cyclesAllowed = $cyclesAllowed;
    }

    public function process() {
        $this->resultCycles = [];
        $this->resultOk = [];
        $this->resultNotTerminated = [];
        $this->collectTestCases();
        return [
            self::RESULT_CYCLES => $this->resultCycles,
            self::RESULT_OK => $this->resultOk,
            self::RESULT_NOT_TERMINATED => $this->resultNotTerminated
        ];
    }

    private function collectTestCases($xml = null, $out = []) {
        if ($xml === null) {
            $xml = $this->rootXml;
        }
        $out[] = (string)$xml['TEXT'];
        if ($xml->count() > 0) {
            foreach ($xml->children() as $child) {
                $this->collectTestCases($child, $out);
            }
        } else {
            $this->validateTestCase($out);
        }
    }

    private function validateTestCase($testCases) {
//        echo "\n--\n";
//        echo implode("\n", $testCases);
        if (count($testCases) === 0) {
            throw new Exception("Testcase is empty");
            return;
        }
        $flowNodes = [];
        foreach ($testCases as $nodeTitle) {
            $flowNode = new FlowNode($nodeTitle);
            if (!isset($flowNodes[$flowNode->getTitle()])) {
                $flowNodes[$flowNode->getTitle()] = 1;
            } else {
                $flowNodes[$flowNode->getTitle()] += 1;
            }
            if ($flowNodes[$flowNode->getTitle()] > $this->cyclesAllowed
) {
//                echo "WARN: Cycle found\n";
                $this->resultCycles[] = $testCases;
                return;
            }
        }

        $lastNode = new FlowNode($testCases[count($testCases) - 1]);
        if ($lastNode->getType() === FlowNode::TYPE_REF) {
            $node = find_node($this->rootXml, $lastNode->getRef());
            if ($node === false) {
//                echo "ERROR: Unknown reference: {$lastNode->getNodeTitle()}\n";
                throw new Exception("Unknown reference: {$lastNode->getNodeTitle()}");
            }
            $this->collectTestCases($node, $testCases);
        } elseif ($lastNode->getType() !== FlowNode::TYPE_END) {
            echo "ERROR: Flow was not terminated properly in {$lastNode->getTitle()}\n";
            $this->resultNotTerminated[] = $testCases;
        } else {
//            echo "ok\n";
            $this->resultOk[] = $testCases;
        }
    }

}


function generate_test_cases($xml, $rootNode, $cycles) {
    $flowNode = find_node($xml, $rootNode);
    if ($flowNode === null) {
        echo 'Flow node not found';
        return;
    }

    $detector = new TestCaseDetector($flowNode, $cycles);
    $result = $detector->process();

    foreach ($result[TestCaseDetector::RESULT_OK] as $k => $testCase) {
        echo "TestCase #" . ($k + 1) . "\n - ";
        echo implode("\n - ", $testCase) . "\n\n";
    }
}
