bash ./scripts/register_protocol.sh TelemetryProtocol examples.telemetry_square.telemetry_protocol

python3 protocol_testing.py --n 4 --protocol TelemetryProtocol TelemetryProtocol TelemetryProtocol TelemetryProtocol --pos [100,100,50] [100,-100,50] [-100,-100,50] [-100,100,50]