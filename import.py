from datetime import date, datetime
from pprint import pprint

from jira import JIRA
from shell import query_nodes



USERS = {
	'@Sheremetov': 'denis',
	'@Durach': 'dmitry',
	'@Bandurka': 'vladimir.bandurka',
	'@Baranov': 'vladislav.baranov',
	'@Boiko': 'roman.boiko',
	'@Chumachenko': 'oleg',
	'@Demchenko': 'dima.demchenko',
	'@DzubenkoE': 'eugen.dzubenko',
	'@Fedorenko': 'alexandr.fedorenko',
	'@Godun': 'dmitriy.godun',
	'@Holin': 'sergey',
	'@Holovlev': '',
	'@Ivanchenko': 'alexander.ivanchenko',
	'@Ivanov': 'andrey.ivanov',
	'@Ivanvhenko': 'alexander.ivanchenko',
	'@Kramarenko': 'vyacheslav.kramarenko',
	'@Levoshko': 'illya.levoshko',
	'@Liya': 'liya.lytvynenko',
	'@Makarevich': 'kela',
	'@Miniaicheva': 'tatiana.miniaicheva',
	'@Nepokrytyi': 'anton.nepokrytyi',
	'@Nevmerzhitskaya': 'svetlana.n',
	'@Omeliukh': 'alona.omeliukh',
	'@Osipov': 'aleksandr.osipov',
	'@Palesika': 'eugene.palesika',
	'@Petluk': 'maxim.petlyuk',
	'@Piskun': 'romanp',
	'@Pritula': 'sergey.pritula',
	'@Rappova': 'nadiia.rappova',
	'@Sagal': 'ivan',
	'@Savchenko': 'vitaliy.savchenko',
	'@Senichkin': 'denis.senichkin',
	'@Sheremetov': 'denis',
	'@Shymko': 'victor.shymko',
	'@Stifutina': '',
	'@Sveta': 'svetlana.n',
	'@Tarasov': '',
	'@Tipa': 'oleg.tipa',
	'@Ukraintsev': 'vlad.ukraintsev',
	'@Zagorsky': 'roman.zagorsky'	
}


options = {
    'server': 'https://onix-systems.atlassian.net'
}
jira = JIRA(options, basic_auth=('denis@onix-systems.com', 'ucqAm6oS63BPXFcsKL6s'))

# Delete all issues
for issue in jira.search_issues('project=GOAL'):
    # print('{}: {}'.format(issue.key, issue.fields.summary))
    issue.delete()


# 2019-01-16 customfield_11315 # start
# 2019-01-24 customfield_11316 # end
# 2019-01-31 duedate

# new_issue = jira.create_issue(project='GOAL', summary='New issue from jira-python',
#                               description='Look into this one', issuetype={'name': 'Bug'})


result = query_nodes('D:\Denis\python\onixteam\Goals.mm', select='assigned', filter='icon-button_ok')
for i in result:

	user = USERS[i.get_attr('Assigned')]
	if user == '':
		continue

	issue_dict = {
	    'project': 'GOAL',
	    'summary': "%s / %s" % (i.get_parent().get_title(), i.get_title()),
	    'description': 'Assigned: %s\n\n%s' % (i.get_attr('Assigned'), i.get_content()),
	    'issuetype': {'name': 'Task'},
	    'assignee': {'name': user}
	}

	if i.has_attr('Start'):
		issue_dict['customfield_11315'] = date.strftime(i.get_attr('Start'), "%Y-%m-%d")

	if i.has_attr('Due'):
		issue_dict['duedate'] = date.strftime(i.get_attr('Due'), "%Y-%m-%d")

	# pprint(issue_dict)
	new_issue = jira.create_issue(fields=issue_dict)

	print(i.get_title())
    # print(i.get_title(), USERS[i.get_attr('Assigned')], i.get_content())
