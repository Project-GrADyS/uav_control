bash ./scripts/register_protocol.sh GroundProtocol examples.simple.protocol_ground
bash ./scripts/register_protocol.sh MobileProtocol examples.simple.protocol_mobile
bash ./scripts/register_protocol.sh SensorProtocol examples.simple.protocol_sensor

python3 protocol_testing.py --n 9 --protocol GroundProtocol MobileProtocol MobileProtocol MobileProtocol MobileProtocol SensorProtocol SensorProtocol SensorProtocol SensorProtocol --pos [-69,0,10] [-69,0,10] [-39,-30,10] [-39,30,10] [-9,-60,10] [-39,-30,10] [-39,30,10] [-9,-60,10] [-9,60,10]