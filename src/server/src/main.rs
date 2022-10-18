#![crate_name = "server"]

fn handle_put(sub: &zmq::Socket) {
    let envelope = sub.recv_string(0).unwrap().unwrap();
    print!("Got message: [{}]", envelope);
    let message = sub.recv_string(0).unwrap().unwrap();
    println!("{}", message);
}

fn handle_sub(sub: &zmq::Socket,reply: &zmq::Socket, topic: &[u8]) -> Result<(), zmq::Error> {
    println!("subscribed to [{}]", topic.escape_ascii());
    sub.set_subscribe(topic).unwrap();
    let ack = String::from("ACK: Subscribed sucesfully");
    reply.send_multipart([&ack], 0)
}

fn handle_unsub(sub: &zmq::Socket,reply: &zmq::Socket, topic: &[u8]) -> Result<(), zmq::Error> {
    println!("unsubscribed from [{}]", topic.escape_ascii());
    sub.set_unsubscribe(topic).unwrap();
    let ack = String::from("ACK: Unsubscribed sucesfully");
    reply.send_multipart([&ack], 0)
}

fn handle_get() {
    
}

fn handle_request(req: &zmq::Socket, sub: &zmq::Socket) -> Result<(), zmq::Error> {
    let messages = req.recv_multipart(0).unwrap();
    println!("Got request:");
    for message in &messages {
        println!("text: {}", message.escape_ascii());
    }
    let request = std::str::from_utf8(messages.get(0).unwrap()).unwrap();
    match request {
        "sub" => {
            let topic = &messages.get(1).unwrap()[..];
            handle_sub(sub,req , topic)
        }
        "unsub" => {
            let topic = &messages.get(1).unwrap()[..];
            handle_unsub(sub, req, topic)
        }
        "get" => {
            Ok(handle_get())
        }
        _ => Err(zmq::Error::ENOBUFS) //fix
    }
}

fn main() {
    let context = zmq::Context::new();
    let reply = context.socket(zmq::REP).expect("failed to create router socket");
    let sub = context.socket(zmq::SUB).expect("failed to create sub socket");

    reply.bind("tcp://*:5563").expect("couldn't bind router socket");
    sub.bind("tcp://*:5564").expect("couldn't bind sub socket");

    println!("ok. looping...");

    loop {
        let mut items = [
            reply.as_poll_item(zmq::POLLIN),
            sub.as_poll_item(zmq::POLLIN),
        ];
        zmq::poll(&mut items, -1).unwrap();
        println!("here!!");
        if items[0].is_readable() {
            handle_request(&reply, &sub).unwrap();
        }
        if items[1].is_readable() {
            handle_put(&sub);
        }
    }
}
