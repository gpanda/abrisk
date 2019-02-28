#!/bin/sh
export nprocs=`getconf _NPROCESSORS_CONF`
export nprocs=`expr 2 '*' $nprocs`
