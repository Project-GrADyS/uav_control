bash ./scripts/register_protocol.sh FollowerProtocol protocol_examples.follow-mobility.follower_protocol
bash ./scripts/register_protocol.sh LeaderProtocol protocol_examples.follow-mobility.leader_protocol

python3 simulation/protocol_testing.py --n 5 --protocol LeaderProtocol FollowerProtocol FollowerProtocol FollowerProtocol FollowerProtocol  --pos [0,0,10] [-5,-5,5] [5,-5,5] [5,5,5] [-5,5,5]