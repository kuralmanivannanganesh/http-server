import socket  # noqa: F401
import threading
import os
import argparse
from pathlib import Path

SERVER = "localhost"
PORT = 4221
ADDR = (SERVER, PORT)
MSG_LENGTH = 1024


'''
An HTTP request is made up of three parts, each separated by a CRLF (\r\n):

Request line. 
Zero or more headers, each ending with a CRLF.
Optional request body.
'''
def send_res_message(conn, msg, content_type = "text/plain"):
    data_len = len(msg)
    res = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {data_len}\r\n\r\n{msg}"
    conn.sendall(res.encode())


def send_res_not_found(conn):
    conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

def send_res_created(conn):
    conn.sendall(b"HTTP/1.1 201 Created\r\n\r\n")

def parse_headers(data):
    headers = {}
    header_lines = data.split("\r\n")
    for line in header_lines:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return headers

def process_file(conn,directory, file_name):
    if not os.path.exists(f"{directory}{file_name}"):
        send_res_not_found(conn=conn)
    else:
        with open(f"{directory}{file_name}", "r") as f:
            content = f.read()
        send_res_message(conn=conn, msg=content,content_type="application/octet-stream") 

def write_file(conn,body, directory, file_name):
    file_path = Path(f"{directory}{file_name}")
    file_path.touch(exist_ok=True)
    file_path.write_text(body)
    send_res_created(conn=conn)


def handle_request(conn, addr, arguments):
    message = conn.recv(MSG_LENGTH).decode()
    print(f"[RAW MESSAGE] : {message}")
    message_split = message.split("\r\n")
    print(f"[SPLIT MESSAGE] : {message_split}")

    req_line = message_split[0]
    recource = req_line.split(" ")[1]
    rec_type = req_line.split(" ")[0]

    if recource == "/":
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif recource.startswith("/echo"):
        data = recource.split("/")[2]
        send_res_message(conn=conn, msg=data)
    elif recource.startswith("/user-agent"):
        headers = parse_headers(message)
        if "user-agent" in headers:
            send_res_message(conn=conn, msg=headers.get("user-agent"))
    elif recource.startswith("/files"):
        file_name = recource.split("/")[2]
        if rec_type == "GET":
            process_file(conn,arguments.directory, file_name)
        elif rec_type == "POST":
            body = message_split[-1]
            write_file(conn, body,arguments.directory, file_name )
    else:
        send_res_not_found(conn=conn)
    conn.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser(description="process arguments")
    parser.add_argument("--directory",
                        type=str,
                        help="Directory path")
    arguments = parser.parse_args()

    # TODO: Uncomment the code below to pass the first stage
    #
    server_socket = socket.create_server(ADDR, reuse_port=True)
    while True:
        conn, addr = server_socket.accept() # wait for client
        threading.Thread(target=handle_request, args=(conn, addr, arguments)).start()
        

if __name__ == "__main__":
    main()
