#![crate_name = "client"]

use core::panic;
use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::env;

fn atoi(s: &str) -> i64 {
    s.parse().unwrap()
}

fn connect(addr: &str) -> zmq::Socket {
    let context = zmq::Context::new();
    let socket = context.socket(zmq::SUB).unwrap();
    assert!(socket.connect(addr).is_ok());
    socket
}

// put [-m/-f] <message/file> <topic_name>
// get [-m/-f] <message/file> <topic_name>
// subscribe <topic_name>
// unsubscribe <topic_name>

fn parse_put_get(args: Vec<String>) -> (String, String){
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

fn parse_subscribe_unsubscribe(args: Vec<String>) -> String {
    if args.len() != 3 {
        panic!("incorrect number of arguments.\nUsage: subscribe <topic_name>");
    }
    String::from(&args[2])
}

fn parse_args(args: Vec<String>) -> (String, String, String) {
    if args.len() < 2 || args.len() > 5 {
        panic!("Usage:\n  put [-m/-f] <message/file> <topic_name>\n  get <topic_name>\n  subscribe <topic_name>\n  unsubscribe <topic_name>");
    }
    let mode = String::from(&args[1]);
    match mode.as_str() {
        "put" => {
            let (msg, topic) = parse_put_get(args);
            (mode, msg, topic)
        }
        "get" => {
            let (msg, topic) = parse_put_get(args);
            (mode, msg, topic)
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
            panic!("Usage:\n  put [-m/-f] <message/file> <topic_name>");
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    parse_args(args);
}