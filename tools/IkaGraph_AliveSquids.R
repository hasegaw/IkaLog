#!Rscript
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Usage:
#    ./IkaGraph_AliveSquids.R lifelog_20150825_2156
#

src_csv = commandArgs(trailingOnly=TRUE)[1]

file_team1 = paste(src_csv, "_team0.csv", sep="")
file_team2 = paste(src_csv, "_team1.csv", sep="")
csv1 <- read.csv(file_team1)
csv2 <- read.csv(file_team2)

output_filename = paste(src_csv, ".png", sep = "")
png(output_filename, width=800, height=600)

y_lim = c(0, 10)
par(xaxt="n")
par(pch=20)

plot(0, 0, type = "n", xlim = c(0, max(0, max(csv1$tick))), ylim = c(0, 10),xlab = "tick", ylab = "", bg = "black")
points(x=csv1$tick, y= 5 + csv1$y, col='blue')
points(x=csv2$tick, y=csv2$y, col='orange')
dev.off()
