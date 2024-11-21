bash ./scripts/register_protocol.sh GroundProtocol protocol_examples.simple.protocol_ground
bash ./scripts/register_protocol.sh MobileProtocol protocol_examples.simple.protocol_mobile
bash ./scripts/register_protocol.sh SensorProtocol protocol_examples.simple.protocol_sensor

python3 simulation/protocol_testing.py --n 9 --protocol GroundProtocol MobileProtocol MobileProtocol MobileProtocol MobileProtocol SensorProtocol SensorProtocol SensorProtocol SensorProtocol --pos [-69,0,10] [-69,0,10] [-39,-30,10] [-39,30,10] [-9,-60,10] [-39,-30,10] [-39,30,10] [-9,-60,10] [-9,60,10]