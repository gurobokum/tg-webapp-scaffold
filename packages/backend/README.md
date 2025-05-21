## TG WebApp scaffold backend

### MinIO

Add this policy localy for access key

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["admin:*"]
    },
    {
      "Effect": "Allow",
      "Action": ["kms:*"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::*"]
    }
  ]
}
```
