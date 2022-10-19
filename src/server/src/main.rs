#![crate_name = "server"]

use std::collections::HashMap;

fn handle_put(sub: &zmq::Socket) {
    let envelope = sub.recv_string(0).unwrap().unwrap();
    print!("Got message: [{}]", envelope);
    let message = sub.recv_string(0).unwrap().unwrap();
    println!("{}", message);
}

fn handle_sub(reply: &zmq::Socket, topic: &[u8], topics: &mut HashMap<String,Vec<String>>, sub_id : String) -> Result<(), zmq::Error> {
    println!("subscribed to [{}]", topic.escape_ascii());
    let topic = String::from_utf8(topic.to_vec()).unwrap();

    let mut ack = String::from("ACK: Subscribed sucesfully");
    if topics.contains_key(&topic) {
        let topic_vec = topics.get(&topic).unwrap();
        if topic_vec.contains(&sub_id) {
            ack = String::from("ACK: Already subscribed");
        }
        else{
            topics.get_mut(&topic).unwrap().push(sub_id);
        }
    }
    else{
        let mut topic_vec = Vec::new();
        topic_vec.push(sub_id);
        topics.insert(topic, topic_vec);
    }

    //print topics key and value for debug mashallah
    for (key, value) in topics {
        println!("{}: {:?}", key, value);
    }
    reply.send_multipart([&ack], 0)
}

fn handle_unsub(sub: &zmq::Socket,reply: &zmq::Socket, topic: &[u8], topics: &mut HashMap<String,Vec<String>>) -> Result<(), zmq::Error> {
    println!("unsubscribed from [{}]", topic.escape_ascii());
    sub.set_unsubscribe(topic).unwrap();
    let ack = String::from("ACK: Unsubscribed sucesfully");
    reply.send_multipart([&ack], 0)
}

fn handle_get() {
    
}

fn handle_request(req: &zmq::Socket, sub: &zmq::Socket,topics: &mut HashMap<String,Vec<String>>) -> Result<(), zmq::Error> {
    let messages = req.recv_multipart(0).unwrap();
    println!("Got request:");
    for message in &messages {
        println!("text: {}", message.escape_ascii());
    }
    let request = std::str::from_utf8(messages.get(0).unwrap()).unwrap();
    match request {
        "sub" => {
            let topic = &messages.get(1).unwrap()[..];
            let id = &messages.get(2).unwrap()[..];
            let sub_id = String::from_utf8(id.to_vec()).unwrap();
            handle_sub(req ,topic,topics, sub_id)
        }
        "unsub" => {
            let topic = &messages.get(1).unwrap()[..];
            handle_unsub(sub, req, topic,topics)
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
    
    let mut topics: HashMap<String, Vec<String>> = HashMap::new();


    loop {
        let mut items = [
            reply.as_poll_item(zmq::POLLIN),
            sub.as_poll_item(zmq::POLLIN),
        ];
        zmq::poll(&mut items, -1).unwrap();
        println!("here!!");
        if items[0].is_readable() {
            handle_request(&reply, &sub,&mut topics).unwrap();
        }
        if items[1].is_readable() {
            handle_put(&sub);
        }
    }
}
