import psycopg2

# database 연결
conn = psycopg2.connect(
host="localhost",
port="5432",
dbname="library_hana",
user="postgres"
)

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
    cursor = conn.cursor()
    cursor.execute(f"""SELECT books.*, case when rentals.status is null then '대여 가능' else status end as status
                                FROM books 
                                LEFT JOIN rentals on books.id= rentals.book_id 
                                WHERE books.id ={book_id};""")
    rows = cursor.fetchall()
    return rows
#유저 정보 쿼리
def user_query(name):
    cursor = conn.cursor()
    cursor.execute(f"""SELECT *
                            FROM users 
                            WHERE users.name ='{name}';""")
    rows = cursor.fetchall()
    return rows

#도서 대여
def rental_book():

    #book_id, user_id 담을 리스트
    results = []

    #대여할 책 선택
    while True:
        rental_book = int(input("대출하고 싶은 책의 id를 입력하세요:"))
        rows = book_query(rental_book)
        if len(rows) == 0:
            print("아이디가 없습니다.")
        elif rows[0][4] !='대여 가능':
            print("해당 도서는 대여중입니다.")
        elif rows[0][4] =='대여 가능' and len(rows) > 0:
            print("대여 가능합니다.")
            results.append(rental_book)
            break

    #대여하는 사용자명 입력
    while True:
        rental_user = input("사용자 이릅을 입력하세요:")
        rows = user_query(rental_user)
        if len(rows) == 0:
            print("사용자가 없습니다.")
        else:
            # user_id 추가
            results.append(rows[0][0])
            print(rows[0][1], "님으로 대여가 신청되었습니다.")
            break

    #대여 신청 쿼리 작성
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO rentals (book_id, user_id, status) 
                        VALUES ({results[0]},{results[1]},'대여중')
                    ;""")
    conn.commit()
    cursor.close()
    # rental_user = (input("사용자 이름을 입력하세요:"))
    # print(rental_user)

#도서 반납
def return_book():
    cursor = conn.cursor()
    books = []
    # 반납하는 사용자명 입력
    while True:
        rental_user = input("사용자 이릅을 입력하세요:")
        rows = user_query(rental_user)
        if len(rows) == 0:
            print("사용자가 없습니다.")
        else:
            # user_id 추가

            cursor.execute(f"""SELECT r.id, b.title, b.author, b.publisher, r.rental_at
                                FROM rentals as r 
                                LEFT JOIN books as b on r.book_id = b.id 
                                WHERE r.user_id = {rows[0][0]} and r.status = '대여중';""")
            rows = cursor.fetchall()
            print("대여한 도서 목록입니다.")
            for row in rows:
                print("대여 id:", row[0], " / 책 이름:", row[1], " / 책 저자:" , row[2], " / 대여 일자: ", row[4])
                books.append(row[0])
            break
    while True:
        return_id = int(input("반납할 도서의 id를 입력하세요: "))
        if return_id in books:
            cursor.execute(f"""UPDATE rentals 
                                SET 
                                  return_at = now(), 
                                   status = '대여 가능'
                                WHERE 
                                    id = {return_id};""")
            conn.commit()
            break
        else:
            print("해당 도서가 대여목록에 없습니다.")

    cursor.close()


#도서 조회
def check_book():
    book_name = input("도서 이름을 입력하세요:")
    cursor = conn.cursor()
    cursor.execute(f"""SELECT books.*, case when rentals.status is null then '대여 가능' else status end as status
                        FROM books 
                        LEFT JOIN rentals on books.id= rentals.book_id 
                        WHERE title like '%{book_name}%';""")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()


#3. 콘솔을 통해 사용자가 메뉴를 선택할 수 있는 기능입니다.
while True:
    print_menu()
    choice = input("원하는 서비스를 선택하세요:")
    if choice == '1':
        check_book()
    elif choice == '2':
        rental_book()
    elif choice =='3':
        return_book()
    elif choice in menu:
        print(f"{choice}. {menu[choice]['name']} 서비스를 선택하셨습니다. ")
    elif choice == '5':
        conn.close()
        print(f"\n서비스를 종료합니다.")
        break
    else:
        print("\n 잘못된 선택입니다. 다시 선택해주세요. ")