# myBookNook Microservice C
# This microservice generates a random ISBN-13 and validates it as a real book
# The ISBN, Title, Author, and Description are returned to the main program

from isbnlib import meta, desc
import random
import zmq

random.seed()

# ISBN-13 checksum algorithm
# Multiply each alternating digit by 1 or 3 and sum the multiplications
# Find the remainder of the sum divided by 10 to get our checksum digit
def isbn_checksum(cur_isbn):
    total = 0
    for index, num in enumerate(cur_isbn):
        if index % 2 == 0:
            total += (num * 1)
        else:
            total += (num * 3)

    remainder = total % 10
    if remainder == 0:
        return 0
    else:
        return 10 - remainder

# Generate a random, but valid, ISBN using the ISBN-13 patterns
def create_isbn():
    new_isbn = [9, 7, random.choice([8, 9])]

    if new_isbn[-1] == 8:
        new_isbn.append(random.choice([0,1]))
    else:
        new_isbn.append(8)

    for i in range(8):
        new_isbn.append(random.randint(0,9))

    new_isbn.append(isbn_checksum(new_isbn))

    isbn_string = "".join(map(str, new_isbn))

    return isbn_string

# Parse book metadata and create a dictionary with the info to be returned to the main program
def get_book_dict(book_meta):
    book_info = {}
    for key, value in book_meta.items():
        match key:
            case "ISBN-13":
                book_info["isbn"] = value
            case "Title":
                book_info["title"] = value
            case "Authors":
                book_info["author"] = value[0]
    book_info["description"] = desc(isbn)

    return book_info


# Establish a socket to receive client connections
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

while True:
    new_req = socket.recv_string()
    print(f"Received request from the client: {new_req}")
    if new_req == "Q":
        print("Ending connection.")
        break

    while True:
        isbn = create_isbn()
        book_data = meta(isbn)
        if book_data:
            break

    book_dict = get_book_dict(book_data)
    socket.send_json(book_dict)

context.destroy()
