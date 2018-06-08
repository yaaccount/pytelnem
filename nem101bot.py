#!/usr/bin/python

import os, io, sys, json, re
import telegramAPI
import persistence
import Nis

telegramAPI.TOKEN = 'YOUR_TOKEN_GOES_HERE'
telegramAPI.URL = 'https://api.telegram.org/bot' + telegramAPI.TOKEN
telegramAPI.WEBHOOK_URL = 'https://YOUR_IP_OR_DOMAIN_GOES_HERE/cgi-bin/telegram/nem101bot.py'
ADMIN_TOKEN = 'YOUR_ADMIN_PASSORD_GOES_HERE' #TODO:

ENABLED = True
DEBUGMODE = False
MINANSWERS = 3

#m = telegramAPI.SetWebhook()
#m.invoke()
#sys.exit()

received = sys.stdin.read()

def parseNemAddress(candidate):
    for addr in re.findall('[NT][A-D][2-9A-Z]{38}', candidate.replace('-','')):
       return addr
    return None

def parseSolution(candidate, minmatches):
    matches = re.findall('\d+[a-z]',candidate.lower())
    if (len(matches) >= minmatches):
        return ''.join(matches)
    else:
        return None

def parsePrizePlan(definition_array):
    _total = 0
    _count = 0
    for n in definition_array:
        if (n.isdigit()):
            i = int(n)
            _count = _count + 1
            _total = _total + i
        else:
            _total = 0
            _count = 0
            break
    return (_total, _count)

#uncomment to log telegram calls
def logTelegramCall(received):
    with io.open('logs/nem101bot.telegram.log', 'a', encoding='utf8') as f:
        #f.write('\nQS: ' + unicode(os.getenv("QUERY_STRING")) + '\n') #raw GET data
        f.write(unicode(received + '\n')) #raw POST data
        f.close()

def logPayout(user, course, solution, rank, award, prefix=''):
    with io.open('logs/nem101bot.payout.log', 'a', encoding='utf8') as f:
        f.write("%sPAYOUT: user: %s(id: %s, tid: %s cid: %s), course: %s(id: %s, solution: %s), address: %s, solution: %s, rank: %s, award: %s)\n" % (prefix, user.detail, str(user.id), user.name, str(user.course_id), course.name, str(course.id), course.solution, user.address, solution, str(rank), str(award)))
        f.close()

class Arguments:
    def __init__(self, telegramUpdate):
        self.chatid = None # to be able to respond
        self.username = None # our unique database token
        self.userdetail = None
        self.text = None # we always respond to something
        self.ok = False # status code
        self.isbot = True # it is not a good idea to talk to bots; it needs to be explicitely set to "False"
        if (telegramUpdate._parsed_ok and telegramUpdate._message != None):
            m = telegramUpdate._message
            if (m._chat != None and m._from != None and m._text != None and len(m._text)>0):
                self.text = m._text
                self.username = m._from._id
                self.userdetail = m._from._first_name + ('' if m._from._last_name == None else ' ' + m._from._last_name) + ('' if m._from._username == None else ' @' + m._from._username)
                self.chatid = m._chat._id
                self.isbot = m._from._is_bot
                if (not self.isbot):
                    self.ok = True
            elif (m._chat != None): # we can at least respond
                self.chatid = m._chat._id

logTelegramCall(received)

#parse the update
telegramUpdate = telegramAPI.Update(received)
args = Arguments(telegramUpdate)

send = 'Unhandled.'

if (not ENABLED):
    send = 'Disabled.'
    args.ok = False

if (DEBUGMODE and args.username==478646818):
    send = 'Maintenance.'
    args.ok = True

if (not args.ok):
    if (args.chatid != None and not args.isbot):
        m = telegramAPI.SendMessage(args.chatid, send)
        m.invoke()
    # exit now; we can not do anything without mandatory arguments
    print("Status: 200\r\n\r\n")
    sys.exit(0)

# get or create user
_persistence = persistence.Persistence('db/nem101bot.db')
_user = persistence.User(args.username)
_persistence.loadOrCreateUser(_user)
if (_user.detail != args.userdetail):
    _user.detail = args.userdetail
    _persistence.storeUser(_user)

cmd = args.text.split()
found = False

# inspect input

# is it command?
if (len(cmd) > 0 and cmd[0].startswith('/')):
    c = cmd[0]                          # command
    a = None if len(cmd)<2 else cmd[1]  # action
    a1 = None if len(cmd)<3 else cmd[2] # argument
    a1full = None if len(cmd)<3 else cmd[2:]
    a1fulltext = None if len(cmd)<3 else (re.match(re.compile('\s*' + cmd[0] + '\s*' + cmd[1] + '\s*(.*)', re.DOTALL), args.text).group(1))
    if (c=='/start' or c=='/i' or c=='/info'):
        send = "user: " + _user.detail + '(' + _user.name + ')'
        if (_user.isadmin):
            send = send + "\nadmin mode ON"
        if (_user.address == None):
            send = send + "\nPlease submit your NEM address"
        else:
            send = send + "\nNEM address: " + _user.address
        if (_user.course_id == None):
            send = send + "\nPlease join a course"
            send = send + "\n(/h for help)"
        else:
            course = persistence.Course(_user.course_id, None)
            _persistence.loadCourse(course)
            send = send + "\ncourse: " + ('' if course.name == None else course.name)
            send = send + "\ndescription:\n" + ('' if course.description == None else course.description)
        found = True
    elif (c=='/nis'):
        send = "chain height:\n"
        txsign = Nis.TxSignService()
        for i in range(0, 3):
            height = txsign.nem.height()
            send = send + ("%s: %s" % (txsign.nem.selected(), height))
            txsign.nem.pickAnotherOne()
        found = True
    elif (c=='/h' or c=='/help'):
        if (_user.isadmin):
            send = (
                '/h - this message'
                '\n/i - your details'
                '\n/j <COURSE_NAME> - join course; you need to join a course to be able to modify it'
                '\n/l [u or c] - list users or courses'
                '\n/c c <COURSE_NAME> - create a new course; join automatically'
                '\n/s [n or d or s or p] - set active course\'s properties: name, description, solution, payout-scheme'
                '\n  description: i.e. include all quiz questions'
                '\n  solution: i.e. 1a2b3c4d - 3 pairs are minimum'
                '\n  payout-scheme: i.e. 3 2 1 1 1 - first five users with right answer (solution) will receive 8 XEM in total; 1st - 3 XEM, 2nd - 2 XEM, etc.'
                '\n/reset - deletes all submitted answers in current course and sets the payed counter to zero; all users can answer and be rewarded again'
            )
        else:
            send = (
                '/h - this message'
                '\n/j <COURSE_NAME> - join a course.'
                '\n/i - your details'
                '\n\nadditionally, you can submit your NEM address or answer to a quiz question (in form 1a2b3c, 3 or more answers are required)'
            )
        found = True
    elif (c=='/god'):
        if (a==ADMIN_TOKEN):
            _user.isadmin = True
            _persistence.storeUser(_user)
            send = 'Admin mode is now ON'
            found = True
        else:
            if (_user.isadmin):
                _user.isadmin = False
                _persistence.storeUser(_user)
                send = 'Admin mode is now OFF'
                found = True
    elif (c=='/j' or c=='/join'):
        if (a!=None):
            _persistence.switchUserToCourse(_user, a)
            if (_user.course_id == None):
                send = 'course ' + a + ' not found'
            else:
                send = 'joined:'
                course = persistence.Course(_user.course_id, None)
                _persistence.loadCourse(course)
                send = send + "\ncourse: " + ('' if course.name == None else course.name)
                send = send + "\ndescription:\n" + ('' if course.description == None else course.description)
        else:
            send = 'please append course name to /j'
        found = True
    else:
        if (_user.isadmin):# Admin mode ON
            if (c=='/l' or c=='/list'): #list
                if (a=='c' or a=='courses'): # courses
                    description = '/l c v - verbose; show full descriptions'
                    verbose = False
                    if (a1=='v' or a1=='verbose'):
                        verbose = True
                    send = 'courses: '
                    for _course in _persistence.getCourses():
                        if (verbose):
                            description = _course.description
                        send = send + ("\n\nName: %s (id: %s)\ndescription: %s\nsolution: %s\npayout: %s\npayed: %s of %s" % (_course.name, str(_course.id), description, _course.solution, _course.prize_definition, str(_course.prize_payed), str(_course.prize_total)))
                elif (a=='u' or a=='users'):
                    if (a1=='v' or a1=='verbose'):
                        send='all users: '
                        for u in _persistence.getUsers():
                            send = send + ("%s(%i;%s), " % (u.detail, 0 if u.course_id is None else u.course_id, u.name))
                    else:
                        send='users in current course: '
                        for u in _persistence.getUsersInCourse(_user.course_id):
                            send = send + ("%s(%i;%s), " % (u.detail, 0 if u.course_id is None else u.course_id, u.name))
                        send = send + '\n/l u v - verbose; show all users'
                else:
                    send='you can list courses (c) or users (u)'
                found = True
            elif (c=='/c' or c=='/create'):
                if (a=='c' or a=='course'): # course
                    if (a1==None):
                      a1='NEM101'
                    _course = persistence.Course(None, a1)
                    _persistence.loadOrCreateCourse(_course)
                    send = 'created course ' + a1
                    _persistence.switchUserToCourse(_user, a1)
                    send = send + '; joined'
                else:
                    send = 'you can create course (c)'
                found = True
            elif (c=='/reset'):
                if (_user.course_id == None):
                    send = 'please join a course where you want to delete all answers'
                else:
                    _persistence.deleteAnswersForCourse(_user.course_id)
                    send = 'done'
                found = True
            elif (c=='/s' or c=='/set'): # set
                _course = persistence.Course(_user.course_id, None)
                if (_persistence.loadCourse(_course)):
                    changed = False
                    kickall = False
                    if (a=='n' or a=='name'):
                        if (a1 != None):
                            _course.name = a1
                            changed = True
                            kickall = True
                    elif (a=='d' or a=='description'):
                        if (a1 != None):
                            _course.description = a1fulltext
                            changed = True
                    elif (a=='s' or a=='solution'):
                        if (a1 != None):
                            _course.solution = a1
                            changed = True
                    elif (a=='p' or a=='payout'):
                        if (a1full != None):
                            (total, count) = parsePrizePlan(a1full)
                            if (total > 0 and count > 0):
                                _course.prize_definition = " ".join(a1full)
                                _course.prize_total = total
                                _course.prize_payed = 0
                                changed = True
                    else:
                        pass
                    if (changed):
                        _persistence.storeCourse(_course)
                        send = "saved changes"
                        if (kickall):
                            _persistence.kickAllFromCourseExceptUser(_course, _user)
                            send = send + "; kicked others"

                    else:
                        send = "no change"
                else:
                    send = ("course %i not found" % (_user.course_id))
                found = True
            else:
                send = 'unknown admin command ' + c
                found = True
        else:
            send = 'unknown command ' + c
            found = True
# no, it is not command; try to find something interresting
else:
    addr = parseNemAddress(args.text)
    if (addr != None):
        _user.address = addr
        _persistence.storeUser(_user)
        send = 'NEM address ' + addr + ' stored.'
        found = True

    if (not found):
        solution = parseSolution(args.text, MINANSWERS)
        if (solution != None):
            if (_user.course_id == None):
                send = 'solution ' + solution + ' not accepted - please join a course (/j)'
            elif (_user.address == None):
                send = 'solution ' + solution + ' not accepted - please submit your NEM address'
            else:
                _course = persistence.Course(_user.course_id, None)
                _persistence.loadCourse(_course)
                # log all answers, also wrong ones; do we want this?
                count = _persistence.submitAnswer(_user, solution)
                send = 'Submitted solution: ' + solution
                if (count == 1):
                    (rank, award) = _persistence.checkAndMaybeAwardUser(_user, solution)
                    if (rank>=0 and _course.solution==solution): # important condition; rank is the same even if wrong answer is given _after_ the right one
                        send = send + '\n\nCorrect.'
                        send = send + '\nRank: ' + str(rank+1)
                        send = send + '\nPrice: ' + str(award) + ' XEM'
                        if (award > 0):
                            # log this first, so we can analyze logs if actual payout fails
                            _course = persistence.Course(_user.course_id, None)
                            _persistence.loadCourse(_course)
                            logPayout(_user, _course, solution, rank, award)
                            txsign = Nis.TxSignService()
                            #print(str(award) + ' -> ' + _user.address)
                            if (not txsign.simplesendXEM(award, '', _user.address)):
                                send = send + '\n\nError: Something is wrong with signing service.'
                                # and log error
                                logPayout(_user, _course, solution, rank, award, 'Error: ')
                    else:
                        send = send + "\n\nIncorrect."
                else:
                    send = send + '. Again. Ignored.'
                found = True

#if (not found):
#  send = 'Ignored.'

_persistence.close()

if (len(send) > 4096):
    pass
    send = send[-4085:] + "<truncated>"

m = telegramAPI.SendMessage(args.chatid, send)
m.invoke()

#print(str(args.chatid) + ' -> ' + send.encode('utf8'))

print("Status: 200\r\n\r\n")

sys.stdout.flush()
sys.exit(0)
