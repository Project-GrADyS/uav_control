bash ./scripts/register_protocol.sh TimeProtocol protocol_examples.time_square.time_protocol

python3 simulation/protocol_testing.py --n 4 --protocol TimeProtocol TimeProtocol TimeProtocol TimeProtocol --pos [100,100,50] [100,-100,50] [-100,-100,50] [-100,100,50]