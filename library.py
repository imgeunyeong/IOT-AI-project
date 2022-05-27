import time

result=[] #검색결과 저장
basket=[] #장바구니에 저장

# 0: 대여불가, 1: 대여가능 
BookList=[[1, '작별인사', '김영하', 1],
          [2, '이기적 유전자', '리처드 도킨스', 1],
          [3, '게놈 익스프레스', '조진호', 1],
          [4, '데미안', '헤르만 헤세', 1],
          [5, '언어의 온도', '이기주', 1],
          [6, '나미야 잡화점의 기적', '히가시노 게이고', 1],
          [7, '인간 실격', '다자이 오사무', 1]]

def rental():
        print(basket)
        user_input=str(input('대여하시겠습니까? y/n'))
        if user_input =='y' or user_input=='Y':
            for i in range(0, len(BookList)):
                for j in range(0, len(basket)):
                    if basket[j]==BookList[i][1]:
                        print(basket[j])
                        BookList[i][3]=0
                        time.sleep(2)
                        print("대여완료")
                        time.sleep(2)
                        del basket[:]
        elif user_input=='n' or user_input=='N':
            print('메인으로 돌아갑니다')
            time.sleep(2)
            menu()  
            
def SearchBookName(user_input):
    for i in range(0, len(BookList)):
        if user_input in BookList[i][1]:
            if BookList[i][3] == 1:
                result.append(BookList[i][1])
                #print(result) #테스트
                ShoppingBasket()
            elif BookList[i][3]==0:
                print(BookList[i][1],end="")
                print(" 대여중")
                time.sleep(2)
                
def SearchBookAuthor(user_input):
    for i in range(0, len(BookList)):
        if user_input in BookList[i][2]:
            if BookList[i][3] == 1:
                result.append(BookList[i][1])
                #print(result) #테스트 
                ShoppingBasket()
            elif BookList[i][3]==0:
                print(BookList[i][1],end="")
                print(" 대여중")
                time.sleep(2)
                
def ShoppingBasket():
    print(result)
    user_input=input('장바구니에 추가하시겠습니까? y/n ')
    if user_input=='y' or user_input=='Y':
        basket.append(result[0])
        print(basket) #테스트
        del result[:]
        time.sleep(2)
        
def menu():
    print('1. 조회')
    print('2. 대여')
    user_input=int(input('선택: '))
    if user_input == 1:
        print('1. 제목')
        print('2. 작가')
        user_input=int(input('선택: '))            
        if user_input == 1:
            user_input=input('제목: ')
            SearchBookName(user_input)
        elif user_input == 2:
            user_input=input('작가: ')
            SearchBookAuthor(user_input)
    elif user_input==2:
        rental()
        
            
while(1):
    menu()