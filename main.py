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

#기능1. 도서 조회
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
    elif choice in menu:
        print(f"{choice}. {menu[choice]['name']} 서비스를 선택하셨습니다. ")
    elif choice == '5':
        conn.close()
        print(f"\n서비스를 종료합니다.")
        break
    else:
        print("\n 잘못된 선택입니다. 다시 선택해주세요. ")