#![crate_name = "client"]

use core::panic;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::env;

fn connect(id: u8, addr: &str) -> zmq::Socket {
    let context = zmq::Context::new();
    let socket = context.socket(zmq::SUB).unwrap();
    socket.set_identity(&[id]).unwrap();
    assert!(socket.connect(addr).is_ok());
    socket
}

fn message_to_server(socket: &zmq::Socket, message: &str) -> String {
    socket.send(message, 0).unwrap();
    let response = socket.recv_string(0).unwrap().unwrap();
    response
}

fn put(socket: &zmq::Socket, key: &str, value: &str) -> String {
    let message = format!("PUT {} {}", key, value);
    message_to_server(socket, &message)
}

fn get(socket: &zmq::Socket, key: &str) -> String {
    let message = format!("GET {}", key);
    message_to_server(socket, &message)
}

fn subscribe(socket: &zmq::Socket, key: &str) -> String {
    let message = format!("SUBSCRIBE {}", key);
    message_to_server(socket, &message)
}

fn unsubscribe(socket: &zmq::Socket, key: &str) -> String {
    let message = format!("UNSUBSCRIBE {}", key);
    message_to_server(socket, &message)
}

// put [-m/-f] <message/file> <topic_name>
// get [-d/-f] (file) <topic_name>
// subscribe <topic_name>
// unsubscribe <topic_name>

fn parse_put(args: Vec<String>) -> (String, String){
    if args.len() != 5 {
        panic!("incorrect number of arguments.\nUsage: put [-m/-f] <message/file> <topic_name>");
    }

    let msg_type = String::from(&args[2]);
    let msg;
    match msg_type.as_str() {
        "-m" => {
            msg = String::from(&args[3]);
        },
        "-f" => {
            let path = Path::new(&args[3]);
            let mut file = match File::open(&path) {
                Err(why) => panic!("couldn't open {}: {}", path.display(), why),
                Ok(file) => file,
            };
            let mut s = String::new();
            match file.read_to_string(&mut s) {
                Err(why) => panic!("couldn't read {}: {}", path.display(), why),
                Ok(_) => msg = String::from(s),
            };
        },
        _ => {
            panic!("incorrect flag.\nUsage: put [-m/-f] <message/file> <topic_name>");
        }
    }
    let topic = String::from(&args[4]);
    (msg, topic)
}

fn parse_get(args: Vec<String>) -> (String, String){
    if args.len() != 5 {
        panic!("incorrect number of arguments.\nUsage: get [-m/-f] <message/file> <topic_name>");
    }
    let msg_store = String::from(&args[2]);
    let path;
    match msg_store.as_str() {
        "-d" => {
            path = String::from("");
        },
        "-f" => {
            path = String::from(&args[3]);
        },
        _ => {
            panic!("incorrect flag.\nUsage: get [-d/-f] (file) <topic_name>");
        }
    }
    let topic = String::from(&args[4]);
    (path, topic)
}

fn parse_subscribe_unsubscribe(args: Vec<String>) -> String {
    if args.len() != 3 {
        panic!("incorrect number of arguments.\nUsage: subscribe <topic_name>");
    }
    String::from(&args[2])
}

fn parse_args(args: Vec<String>) -> (String, String, String) {
    if args.len() < 2 || args.len() > 5 {
        panic!("Usage:\n  put [-m/-f] <message/file> <topic_name>\n  get [-d/-f] (file) <topic_name>\n  subscribe <topic_name>\n  unsubscribe <topic_name>");
    }
    let mode = String::from(&args[1]);
    match mode.as_str() {
        "put" => {
            let (msg, topic) = parse_put(args);
            (mode, msg, topic)
        }
        "get" => {
            let (path, topic) = parse_get(args);
            (mode, path, topic)
        }
        "subscribe" => {
            let topic = parse_subscribe_unsubscribe(args);
            (mode, String::from(""), topic)
        }
        "unsubscribe" => {
            let topic = parse_subscribe_unsubscribe(args);
            (mode, String::from(""), topic)
        }
        _ => {
            panic!("Usage:\n  put [-m/-f] <message/file> <topic_name>\n  get [-d/-f] (file) <topic_name>\n  subscribe <topic_name>\n  unsubscribe <topic_name>");
        }
    }
}

fn store_msg_file(msg: &str, file_path: &str) {
    let path = Path::new(file_path);
    let mut file = match File::create(&path) {
        Err(why) => panic!("couldn't create {}: {}", path.display(), why),
        Ok(file) => file,
    };
    match file.write_all(msg.as_bytes()) {
        Err(why) => panic!("couldn't write to {}: {}", path.display(), why),
        Ok(_) => println!("successfully wrote to {}", path.display()),
    }
}

fn main() {
    let socket = connect(1, "tcp://localhost:5556");
    let args: Vec<String> = env::args().collect();
    let (mode, msg, topic) = parse_args(args);
    match mode.as_str() {
        "put" => {
            put(&socket, &topic, &msg);
        }
        "get" => {
            get(&socket, &topic);
        }
        "subscribe" => {
            subscribe(&socket, &topic);
        }
        "unsubscribe" => {
            unsubscribe(&socket, &topic);
        }
        _ => {
            panic!("Usage:\n  put [-m/-f] <message/file> <topic_name>");
        }
    }
}