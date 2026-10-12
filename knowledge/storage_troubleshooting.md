# Storage Troubleshooting

## Slow performance
Check for drives with growing seek error rates or reallocated sectors, since retries slow down reads. Compare latency across drives in the same array.

## Drive reported degraded
Check telemetry history first. If temperature is normal but sectors are rising, the media is failing. If temperature is high, fix cooling before replacing the drive.

## Repeated incidents on one rack
Look for a shared cause such as cooling, power, or vibration before replacing every drive individually.
