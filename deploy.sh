#!/bin/sh

# sync images(jpg, jpeg, png, gif, svg), css and js 
# to s3://example.com with big max-age
aws s3 sync build s3://$1 --exclude "*" \
--include "*.jpg" --include "*.jpeg" --include "*.png" \
--include "*.gif" --include "*.svg" --include "*.webp" \
--include "*.css" --include "*.js" \
--cache-control "public, max-age=31536000" \
--storage-class INTELLIGENT_TIERING --delete

# sync json, ico, xml, xsl files
# to s3://example.com with small max-age
aws s3 sync build s3://$1 --exclude "*" \
--include "*.json" --include "*.ico" --include "*.xml" \
--include "*.xsl" --cache-control "public, max-age=86400" \
--storage-class INTELLIGENT_TIERING --delete

# sync the rest of the files with no max-age cache
aws s3 sync build s3://$1 --storage-class INTELLIGENT_TIERING --delete