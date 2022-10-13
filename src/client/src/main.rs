#![crate_name = "client"]

use std::env;
use std::thread::sleep;
use std::time::Duration;

fn subscriber(ctx: zmq::Context) {
    let subscriber = ctx.socket(zmq::SUB).unwrap();
    subscriber
        .connect("tcp://localhost:5563")
        .expect("failed connecting subscriber");
    subscriber.set_subscribe(b"B").expect("failed subscribing");

    loop {
        let envelope = subscriber
            .recv_string(0)
            .expect("failed receiving envelope")
            .unwrap();
        print!("[{}]", envelope);
        let message = subscriber
            .recv_string(0)
            .expect("failed receiving message")
            .unwrap();
        println!("{}", message);
    }
}

fn publisher(ctx: zmq::Context) {
    let publisher = ctx.socket(zmq::PUB).unwrap();
    publisher
        .connect("tcp://localhost:5564")
        .expect("failed binding publisher");

    loop {
        publisher
            .send("A", zmq::SNDMORE)
            .expect("failed sending first envelope");
        publisher
            .send("We don't want to see this", 0)
            .expect("failed sending first message");
        publisher
            .send("B", zmq::SNDMORE)
            .expect("failed sending second envelope");
        publisher
            .send("We would like to see this", 0)
            .expect("failed sending second message");
        sleep(Duration::from_millis(1));
    }
}

fn main() {
    let context = zmq::Context::new();

    let args: Vec<String> = env::args().collect();
    
    if &args[1] == "pub" {
        publisher(context);
    } else {
        subscriber(context);
    }
}
