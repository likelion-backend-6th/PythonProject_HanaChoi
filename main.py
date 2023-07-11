import psycopg2

# database 연결
conn = psycopg2.connect(
host="localhost",
port="5432",
dbname="library_hana",
user="postgres"
)
cursor = conn.cursor()

#1. 메인 메뉴 구조 입니다.
menu = {
    '1': {'name':'도서 정보 조회'},
    '2': {'name':'도서 대출'},
    '3': {'name':'도서 반납'},
    '4': {'name':'대출 정보 조회'},
}

#2. 메뉴 프린트 기능입니다.
def print_menu():
    print("-----------------------------")
    print("    도서관 관리 시스템 메인 메뉴    ")
    print("-----------------------------")
    for id, item in menu.items():
        print(f"{id}. {item['name']}")
    print("5. 종료")
#책 정보 쿼리
def book_query(book_id):

    cursor.execute(f"""SELECT books.*, 
                        case when rentals.status is null then '대여 가능'
                             when rentals.status = '반납 완료' then '대여 가능'
                             else status end as status
                                FROM books 
                                LEFT JOIN rentals on books.id= rentals.book_id 
                                WHERE book_id = {book_id};
                                """)
    rows = cursor.fetchall()
    return rows
#유저 정보 쿼리
def user_query(name):

    cursor.execute(f"""SELECT *
                            FROM users 
                            WHERE users.name ='{name}';""")
    rows = cursor.fetchall()
    return rows

# 대출 정보 쿼리
def rental_query(user_name, where_str):

    cursor.execute(f"""SELECT r.id, b.title, b.author, b.publisher, r.rental_at, u.name, r.book_id, r.status,r.return_at
                        FROM rentals as r 
                        INNER JOIN users as u on r.user_id = u.id and u.name = '{user_name}'
                        INNER JOIN books as b on r.book_id = b.id 
                        {where_str}
                        ORDER BY r.id desc;""")
    rows = cursor.fetchall()
    return rows
#도서 대여
def rental_book():

    #book_id, user_id 담을 리스트
    results = []
    #대여할 책 선택
    while True:
        rental_book = int(input("대출하고 싶은 책의 id를 입력하세요 (숫자 0 입력 시 종료):"))
        if rental_book == 0:
            break

        #books와 rentals 테이블에서 책 정보와 대여 현황 리턴
        rows = book_query(rental_book)
        if len(rows) == 0:
            print("해당 도서가 없습니다.")
        elif rows[0][4] != '대여 가능':
            print("해당 도서는 대여중입니다.")
        elif rows[0][4] =='대여 가능':
            print("대여 가능합니다.")
            results.append(rental_book)
            break

    #대여하는 사용자명 입력
    while True:
        rental_user = input("사용자 이름을 입력하세요 (숫자 0 입력 시 종료):")
        if rental_user == '0':
            break

        # users 테이블에서 조회 후 리턴
        rows = user_query(rental_user)
        if len(rows) == 0:
            print("사용자가 없습니다.")
        else:
            # user_id 추가
            results.append(rows[0][0])

            # 대여 신청 쿼리 작성
            # rentals 테이블에 해당 book_id, user_id 에 해당하는 값을 '대여중'상태로 추가
            cursor.execute(f"""INSERT INTO rentals (book_id, user_id, status) 
                                VALUES ({results[0]},{results[1]},'대여중')
                            ;""")
            conn.commit()
            print(rows[0][1], "님으로 대여가 신청되었습니다.")
            break

#도서 반납
def return_book():

    books = []
    user_id = ''
    # 반납하는 사용자명 입력
    while True:
        rental_user = input("사용자 이름을 입력하세요(숫자 0 입력 시 종료):")
        if rental_user=='0':
            break

        rows = user_query(rental_user)
        if len(rows) == 0:
            print("사용자가 없습니다.")
        else:
            # rentals에서 해당유저의 대여중인 도서목록 출력

            user_id = rows[0][0]
            rental_rows = rental_query(rental_user,"WHERE r.status='대여중'")
            print(rental_rows[0][5],"님의 대여중인 도서 목록입니다.")
            for row in rental_rows:
                print("책 ID:", row[6],
                      " / 책 이름:", row[1],
                      " / 책 저자:" , row[2],
                      " / 대여 일자:", row[4])
                books.append(row[6])
            break
    while True:
        book_id = int(input("반납할 도서의 id를 입력하세요 (숫자 0 입력시 종료): "))
        if book_id == 0:
            break

        # 대여목록에 있는 도서인지 확인
        if book_id in books:
            cursor.execute(f"""UPDATE rentals 
                                SET 
                                  return_at = now(), 
                                   status = '반납 완료'
                                WHERE 
                                    book_id = {book_id}
                                    and status = '대여중'
                                    and user_id = {user_id};""")
            conn.commit()
            print("반납 완료되었습니다.")
            break
        else:
            print("해당 도서가 대여목록에 없습니다.")




#도서 조회
def check_book():

    while True:
        book_name = input("도서 이름을 입력하세요 (숫자 0 입력시 종료):")
        if book_name == '0':
            break

        #조회 쿼리
        cursor.execute(f"""SELECT books.*, 
                            case when rentals.status is null then '대여 가능'
                                when rentals.status = '반납 완료' then '대여 가능' 
                            else status end as status
                        FROM books 
                        LEFT JOIN rentals on books.id= rentals.book_id 
                        WHERE title like '%{book_name}%';""")
        rows = cursor.fetchall()

        #조회 값 없음
        if len(rows) ==0:
            print("해당 도서가 없습니다.")
        #조회 값 있음
        else:
            for row in rows:
                print("(",row[4] ,") 책 ID:", row[0],
                      " / 책 이름:", row[1],
                      " / 저자:", row[2],
                      " / 출판사:", row[3])

# 대출 정보 조회
def check_rental():

    while True:
        user_name = input("대출 정보 조회할 사용자 이름을 입력하세요(숫자 0 입력시 종료):")
        if user_name == '0':
            break

        rows = rental_query(user_name," ")
        if len(rows) == 0:
            print("해당 사용자가 없습니다.")
        else:
            for row in rows:
                print("(",row[7],") 대여 id:", row[0]
                      , " / 책 이름:", row[1]
                      , " / 책 저자:", row[2]
                      , " / 대여 일자: ", row[4]
                      , " / 반납 일자: ", row[8])




#3. 콘솔을 통해 사용자가 메뉴를 선택할 수 있는 기능입니다.
while True:
    print_menu()
    choice = input("원하는 서비스를 선택하세요:")
    if choice == '1':
        check_book()
    elif choice == '2':
        rental_book()
    elif choice == '3':
        return_book()
    elif choice == '4':
        check_rental()
    elif choice == '5':
        cursor.close()
        conn.close()
        print(f"\n서비스를 종료합니다.")
        break
    else:
        print("\n 잘못된 선택입니다. 다시 선택해주세요. ")

