#!/usr/bin/bash
awslocal s3 mb s3://test-bucket
awslocal s3 cp /var/lib/localstack/emma.mp3 s3://test-bucket/emma.mp3
