#!/usr/bin/python3

import sys
import sqlite3

#persisted classes
class Course:
    def __init__(self, _id, _name):
        self.id = _id
        self.name = _name
        self.description = None
        self.solution = None
        self.prize_definition = "21 10 10 5 5 5 5 5 5 5 5 5 5 5 5"
        self.prize_total = 101
        self.prize_payed = 0

class User:
    def __init__(self, _name):
        self.id = None
        self.course_id = None
        self.name = _name
        self.address = None
        self.detail = None
        self.isadmin = False

class Answer:
    def __init__(self):
        self.id = None
        self.course_id = None
        self.user_id = None
        self.answer = None
        self.count = 0

class Persistence:
    def __init__(self, _filename):
        self.filename = _filename
        self.conn = sqlite3.connect(self.filename)
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS "
                  "courses ("
                    "id INTEGER PRIMARY KEY, "
                    "name TEXT NOT NULL UNIQUE, "
                    "description TEXT, "
                    "solution TEXT, "
                    "prize_definition TEXT, "
                    "prize_total INTEGER, "
                    "prize_payed INTEGER"
                  ")"
                 )
        c.execute("CREATE TABLE IF NOT EXISTS "
                  "users ("
                    "id INTEGER PRIMARY KEY, "
                    "course_id INTEGER, "
                    "name TEXT NOT NULL UNIQUE, "
                    "detail, "
                    "address TEXT, "
                    "isadmin INTEGER, "
                    "FOREIGN KEY(course_id) REFERENCES courses(id)"
                  ")"
                 )
        c.execute("CREATE TABLE IF NOT EXISTS "
                  "answers ("
                    "id INTEGER PRIMARY KEY, "
                    "course_id INTEGER NOT NULL, "
                    "user_id INTEGER NOT NULL, "
                    "answer TEXT, "
                    "count INTEGER, "
                    "FOREIGN KEY(course_id) REFERENCES courses(id), "
                    "FOREIGN KEY(user_id) REFERENCES users(id)"
                  ")"
                 )

        self.conn.commit()

    def loadCourse(self, _course):
        c = self.conn.cursor()
        if (_course.id == None):
            c.execute("SELECT id, name, description, solution, prize_definition, prize_total, prize_payed FROM courses WHERE name = ?",
                (_course.name, ))
        else:
            c.execute("SELECT id, name, description, solution, prize_definition, prize_total, prize_payed FROM courses WHERE id = ?",
                (_course.id, ))

        row = c.fetchone()
        if (row != None):
            (_course.id, _course.name, _course.description, _course.solution, _course.prize_definition, _course.prize_total, _course.prize_payed) = row
            return True
        else:
            return False

    def storeCourse(self, _course):
        c = self.conn.cursor()
        if (_course.id == None):
            c.execute("INSERT INTO courses(name) VALUES(?)",
                (_course.name, ))
        else:
            c.execute("INSERT OR REPLACE INTO courses(id, name, description, solution, prize_definition, prize_total, prize_payed) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (_course.id, _course.name, _course.description, _course.solution, _course.prize_definition, _course.prize_total, _course.prize_payed, ))
        self.conn.commit()

    def loadOrCreateCourse(self, _course):
        ok = self.loadCourse(_course)
        if (not ok):
            self.storeCourse(_course)
            self.conn.commit()
            self.loadCourse(_course)

    def getCourses(self):
        courses = []
        c = self.conn.cursor()
        c.execute("SELECT id, name, description, solution, prize_definition, prize_total, prize_payed FROM courses")
        for row in c:
            _course = Course(None, 'New')
            (_course.id, _course.name, _course.description, _course.solution, _course.prize_definition, _course.prize_total, _course.prize_payed) = row
            courses.append(_course)
        return courses

    def loadOrCreateUser(self, _user):
        c = self.conn.cursor()
        c.execute("SELECT id, course_id, name, address, detail, isadmin FROM users WHERE name = ?",
            (_user.name, ))
        row = c.fetchone()
        if (row != None):
            (_user.id, _user.course_id, _user.name, _user.address, _user.detail, _user.isadmin) = row
        else:
            self.storeUser(_user)
            self.conn.commit()
            self.loadOrCreateUser(_user)

    def storeUser(self, _user):
        c = self.conn.cursor()
        if (_user.id == None):
            c.execute("INSERT INTO users(name, detail) VALUES(?, ?)",
                (_user.name, _user.detail))
        else:
            c.execute("INSERT OR REPLACE INTO users(id, course_id, name, address, detail, isadmin) VALUES(?, ?, ?, ?, ?, ?)",
                (_user.id, _user.course_id, _user.name, _user.address, _user.detail, _user.isadmin, ))
        self.conn.commit()

    def getUsers(self):
        users = []
        c = self.conn.cursor()
        c.execute("SELECT id, course_id, name, address, detail, isadmin FROM users")
        for row in c:
            _user = User('New')
            (_user.id, _user.course_id, _user.name, _user.address, _user.detail, _user.isadmin) = row
            users.append(_user)
        return users

    def getUsersInCourse(self, _course_id):
        users = []
        c = self.conn.cursor()
        c.execute("SELECT id, course_id, name, address, detail, isadmin FROM users WHERE course_id = ?",
            (_course_id, ))
        for row in c:
            _user = User('New')
            (_user.id, _user.course_id, _user.name, _user.address, _user.detail, _user.isadmin) = row
            users.append(_user)
        return users

    def getAnswers(self):
        answers = []
        c = self.conn.cursor()
        c.execute("SELECT id, course_id, user_id, answer, count FROM answers")
        for row in c:
            _answer = Answer()
            (_answer.id, _answer.course_id, _answer.user_id, _answer.answer, _answer.count) = row
            answers.append(_answer)
        return answers

    def switchUserToCourse(self, _user, _course_name):
        c = self.conn.cursor()
        c.execute("UPDATE users set course_id=(SELECT id FROM courses where name = ?) WHERE id = ?",
            (_course_name, _user.id, ))
        self.loadOrCreateUser(_user)
        self.conn.commit()

    def kickAllFromCourseExceptUser(self, _course, _user):
        c = self.conn.cursor()
        values = (_course.id, _user.id, )
        c.execute("UPDATE users SET course_id=NULL WHERE course_id=? AND id!=?", values)
        self.conn.commit()

    def submitAnswer(self, _user, _answer):
        count = 0
        c = self.conn.cursor()
        values = (_user.id, _user.course_id, _answer, )
        c.execute("SELECT id, count FROM answers WHERE user_id=? AND course_id=? AND answer=?", values)
        row = c.fetchone()
        if (row == None):
            c.execute("INSERT INTO answers(user_id, course_id, answer, count) VALUES(?, ?, ?, 1)", values)
            count = 1
        else:
            (id, count) = row
            values = (id, )
            c.execute("UPDATE answers SET count=count+1 WHERE id=?", values)
            count = count + 1
        self.conn.commit()
        return count

    def deleteAnswersForCourse(self, _course_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM answers WHERE course_id = ?",
            (_course_id, ))
        c.execute("UPDATE courses SET prize_payed=0 WHERE id = ?",
            (_course_id, ))
        self.conn.commit()

    def checkAndMaybeAwardUser(self, _user, solution):
        c = self.conn.cursor()
        award = 0
        rank = None
        count = 0
        course = Course(_user.course_id, None)
        ok = self.loadCourse(course)
        if (ok and course.solution!=None):
            values = ( _user.course_id, course.solution, )
            c.execute("SELECT user_id, count FROM answers WHERE course_id=? AND answer=? ORDER BY id ASC", values)
            index = 0
            for row in c:
                (id, count) = row
                if (id == _user.id):
                    rank = index
                    break
                index = index + 1

        if (rank!=None and count==1):
            prize = 0
            prizes = course.prize_definition.split()
            if (rank < len(prizes)):
                prize = int(prizes[rank])
            prize_left = course.prize_total - course.prize_payed
            if (prize > 0 and prize <= prize_left):
                award = prize
                if (course.solution == solution):
                    course.prize_payed = course.prize_payed + award
                self.storeCourse(course)
        return (rank, award)

    def close(self):
        self.conn.close()

def test(argv):
    p = Persistence('test.db')
    template = Course(None, 'template')
    for n in ["A", "B", "C", "D", "E"]:
        c = Course(None, n)
        p.loadOrCreateCourse(c)
        c.solution = "1a2b3" + n.lower()
        c.prize_definition = template.prize_definition
        c.prize_payed = template.prize_payed
        c.prize_total = template.prize_total

        p.storeCourse(c)

    u1 = User('TestUser')
    p.loadOrCreateUser(u1)
    u2 = User('TestUser2')
    p.loadOrCreateUser(u2)
    u2.address = 'NADDRESS'
    u2.course_id = 1
    p.storeUser(u2)
    p.switchUserToCourse(u1, "D")
    p.switchUserToCourse(u2, "D")
    for u in p.getUsers():
        print("%i, %i, %s, %s, %s, %i" % (u.id, -1 if u.course_id==None else u.course_id, u.name, u.address, u.detail, False if u.isadmin==None else u.isadmin))

    for i in [1, 2, 3]:
        count = p.submitAnswer(u2, "1a2b3d")
        (rank, award) = p.checkAndMaybeAwardUser(u2, '')
        print "rank: %i, award %i" % (-1 if rank==None else rank, award)
        count = p.submitAnswer(u1, "1a2b3z")
        (rank, award) = p.checkAndMaybeAwardUser(u1, '')
        print "rank: %i, award %i" % (-1 if rank==None else rank, award)
        count = p.submitAnswer(u1, "1a2b3d")
        (rank, award) = p.checkAndMaybeAwardUser(u1, '')
        print "rank: %i, award %i" % (-1 if rank==None else rank, award)
    for i in [1, 2, 3]:
        print(p.submitAnswer(u2, "solution " + str(i)))

    for c in p.getCourses():
        print ("%i, %s, %s, %s" % (c.id, c.name, c.solution, c.prize_definition))
#
    for a in p.getAnswers():
        print ("%i, %i, %i, %s, %i" % (a.id, -1 if a.course_id==None else a.course_id, a.user_id, a.answer, a.count))
# execute only if run as a script
if __name__ == "__main__":
    test(sys.argv)
