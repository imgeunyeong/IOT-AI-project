class Student:
    def __init__(self, name, korean, math, english, science):
        self.name=name
        self.korean=korean
        self.math=math
        self.english=english
        self.science=science
        
    def string(self):
        return "{}\t{}\t{}\t{}\t{}".format(self.name,self.korean,self.math, self.english, self.science)

class Score(Student):
    def sum(self):
        return self.korean+self.math+self.english+self.science

    def average(self):
        return self.sum()/4
    
    def string(self):
        return "{}\t{}\t{}".format(self.name,self.sum(),self.average())
    
students=[
    Student("윤인성", 87, 98, 88, 95),
    Student("연화진", 92, 98, 96, 98),
    Student("구지연", 76, 96, 94, 90),
    Student("나선주", 98, 92, 96, 92),
    Student("윤아린", 95, 98, 98, 98),
    Student("윤명필", 64, 88, 92, 92)
]

for students in students:
    print(students.string())