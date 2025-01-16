bash ./scripts/register_protocol.sh MessageProtocol protocol_examples.message_square.message_protocol

python3 simulation/protocol_testing.py --n 4 --protocol MessageProtocol MessageProtocol MessageProtocol MessageProtocol --pos [100,100,50] [100,-100,50] [-100,-100,50] [-100,100,50]