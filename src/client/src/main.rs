#![crate_name = "client"]

use std::fs::File;
use std::io::prelude::*;
use std::path::Path;
use std::env;

const IP_PREFIX: &'static str = "tcp://localhost";
const SUB_PORT: &'static str = "5563";
const PUB_PORT: &'static str = "5564";
const USAGE: &'static str = "Usage:\n  put [-m/-f] <message/file> <topic_name>\n  get <id>\n  subscribe <id> <topic_name>\n  unsubscribe <id> <topic_name>";
const TIMEOUT: i64 = 3000;

enum Operation {
    Put(String, String),
    Get(String),
    Sub(String),
    Unsub(String),
}

struct Request {
    id: String,
    operation: Operation,
}

impl Request {
    fn send(&self, ctx: &zmq::Context) {
        match &self.operation {
            Operation::Put(topic, message) => put(ctx, &topic, &message),
            Operation::Sub(topic) => subscribe(ctx, &self.id, &topic),
            Operation::Unsub(topic) => unsubscribe(ctx, &self.id, &topic),
            Operation::Get(topic) => get(ctx,&topic)
        }
    }
}

fn get_ack(socket: &zmq::Socket) -> Result<String, ()> {
    println!("Waiting for reply...");
    if socket.poll(zmq::POLLIN, TIMEOUT).unwrap() == 0 {
        println!("Timeout!");
        return Err(());
    }
    let response = socket.recv_string(0).expect("failed subscribing").unwrap();
    println!("Received reply: {}", response);
    Ok(response)
}

fn connect(ctx: &zmq::Context, sock_type: zmq::SocketType) -> zmq::Socket {
    let connection = ctx.socket(sock_type).unwrap();
    let port = match sock_type {
        zmq::SocketType::REQ => SUB_PORT,
        zmq::SocketType::PUB => PUB_PORT,
        _ => panic!("unexpected socket type"),
    };
    let address = format!("{}:{}", IP_PREFIX, port);
    connection
        .connect(address.as_str())
        .expect("failed connecting");
    connection
}

fn subscribe(ctx: &zmq::Context, id: &String, topic: &String) {
    let socket = connect(ctx, zmq::REQ);
    socket.send_multipart(["sub", id, topic], 0).expect("failed subscribing");
    get_ack(&socket).unwrap();
}

fn unsubscribe(ctx: &zmq::Context, id: &String, topic: &String) {
    let socket = connect(ctx, zmq::REQ);
    socket.send_multipart(["unsub", id, topic], 0).expect("failed unsubscribing");
    
    get_ack(&socket).unwrap();
}

fn put(ctx: &zmq::Context, topic: &String, message: &String) {
    let socket = connect(ctx, zmq::PUB);
    println!("putting [{}] : {}", topic, message);
    socket.send_multipart([topic, message], 0).unwrap();
}

fn get(ctx: &zmq::Context, topic: &String) {
    let socket = connect(ctx, zmq::REQ);
    socket.send_multipart([topic],0).unwrap();

    let response = socket.recv_multipart(0).unwrap();
    for message in &response{
        println!("text: {}", message.escape_ascii());
    }
}

// put [-m/-f] <message/file> <topic_name>
// get <id>
// subscribe <id> <topic_name>
// unsubscribe <id> <topic_name>

fn parse_put(args: &[String]) -> Operation {
    if args.len() != 3 {
        panic!("incorrect number of arguments.\nUsage: put [-m/-f] <message/file> <topic_name>");
    }
    let msg_type = String::from(&args[0]);
    let msg = match msg_type.as_str() {
        "-m" => String::from(&args[1]),
        "-f" => {
            let path = Path::new(&args[3]);
            let mut file = File::open(&path).expect("couldn't open file");
            let mut s = String::new();
            file.read_to_string(&mut s).expect("couldn't read file");
            s
        },
        _ => {
            panic!("incorrect flag.\nUsage: put [-m/-f] <message/file> <topic_name>");
        }
    };
    let topic = String::from(&args[2]);
    Operation::Put(topic, msg)
}

fn parse_args(args: Vec<String>) -> Request {
    if args.len() < 3 || args.len() > 5 {
        panic!("{}", USAGE);
    }
    let mode = String::from(&args[1]);
    let id = String::from(&args[2]);
    let operation = match mode.as_str() {
        "put" => parse_put(&args[2..]),
        "get" => Operation::Get(args.get(2).expect(USAGE).to_string()),
        "subscribe" => Operation::Sub(args.get(3).expect(USAGE).to_string()),
        "unsubscribe" => Operation::Unsub(args.get(3).expect(USAGE).to_string()),
        _ => panic!("{}", USAGE)
    };
    Request { id, operation }
}

fn store_msg_file(msg: &str, file_path: &str) {
    let path = Path::new(file_path);
    let mut file = File::create(&path).expect("couldn't create file");
    file.write_all(msg.as_bytes()).expect("couldn't write to file");
    println!("successfully wrote to {}", path.display());
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let request = parse_args(args);
    let context = zmq::Context::new();
    request.send(&context);
}