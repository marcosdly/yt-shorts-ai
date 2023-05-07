#! /usr/bin/env bash

cd "$HOME"

mkdir yt-shorts-ai.d

cd yt-shorts-ai.d

# create required directories if they don't exist
mkdir -p \
  .uncutted-videos-input                                    \
  .cutted-videos-pre-validation/{10s,20s,30s,40s,50s,60s}   \
  .rejected-videos                                          \
  .approved-not-posted-videos/{10s,20s,30s,40s,50s,60s}     \
  .approved-already-posted-videos/{10s,20s,30s,40s,50s,60s} \
  .invalid-files-and-dirs-trash                             \
  .yt-shorts.log.d