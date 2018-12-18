### Freemind tools

Python library and commandline tool for work with [freemind mindmaps](http://freemind.sourceforge.net/wiki/index.php/Main_Page)

A few examples of work with library:

Select all nodes below node _Business_ except nodes with icons _button_ok_, _stop-sign_ and without description
```
goals_command('Tasks.mm', select='title:Business', filter='icon-button_ok,icon-stop-sign', description='no')
```

Select all nodes from freemind _Tasks.mm_ that have attribute _assigned_ with value _@Kowalski_ except nodes that has icon _button_ok_
```
todo_command('Tasks.mm', select='assigned:@Kowalski', filter='icon-button_ok')
```

Select node with id _363b6bf92c5df3e2dc30043f1212d103_
```
todo_command('Tasks.mm', select='id:363b6bf92c5df3e2dc30043f1212d103')
```

