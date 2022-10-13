#![crate_name = "server"]

fn main() {
    let context = zmq::Context::new();
    let xpub_socket = context.socket(zmq::XPUB).expect("failed to create pubSocket");
    let xsub_socket = context.socket(zmq::XSUB).expect("failed to create subSocket");

    xpub_socket.bind("tcp://*:5563").expect("couldn't bind XPUB socket");
    xsub_socket.bind("tcp://*:5564").expect("couldn't bind XSUB socket");

    loop {
        let mut items = [
            xpub_socket.as_poll_item(zmq::POLLIN),
            xsub_socket.as_poll_item(zmq::POLLIN),
        ];
        zmq::poll(&mut items, -1).unwrap();
        println!("here!!");
        if items[0].is_readable() {
            let message = xpub_socket.recv_string(0).unwrap().unwrap();
            println!("Got subscription: {}", message);
            xsub_socket.send(message.as_bytes(), 0).unwrap();
        }
        if items[1].is_readable() {
            let envelope = xsub_socket.recv_string(0).unwrap().unwrap();
            print!("Got message: [{}]", envelope);
            let message = xsub_socket.recv_string(0).unwrap().unwrap();
            println!("{}", message);
        }
    }
}
