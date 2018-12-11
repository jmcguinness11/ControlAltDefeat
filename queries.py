########## QUERIES FOR REPORTS ##########

# ex:
#   format totals query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
#   format wins query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
RP_TOTALS_COLS = ['RP', 'PlayCount', 'PlayTotal', 'PlayPercent']
RP_WINS_COLS = ['RP', 'WinCount', 'TotalRP', 'WinPercent']

TOTALS_QUERY_DOWNS = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y' group by rp) wins WHERE  Plays.genFormation != 'victory' {0} and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot WHERE  Plays.genFormation != 'victory' {0} and Plays.rp like 'N' GROUP BY Plays.rp);"


ALL_TOTALS_QUERY = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y'group by rp) wins WHERE  Plays.genFormation != 'victory' and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot WHERE  Plays.genFormation != 'victory' and Plays.rp like 'N' GROUP BY Plays.rp) ;"

# for sitrp
WINS_QUERY_DOWNS = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP',  CONCAT(TRUNCATE(100*count(Plays.rp)/totalRP.Count, 2), '%') as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y' {0}) tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory' {0} and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' {0} and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '-' as RP, '-' as WinCount,'-' as TotalRP, '-' as WinPercent;"

WINS_QUERY = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP', CONCAT(TRUNCATE(100*count(Plays.rp)/totalRP.Count, 2), '%') as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y') tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory'and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '-' as RP,'-' as WinCount,'-' as TotalRP,'-' as WinPercent;"

# MOTION

ALL_MOTION_COLS = ['Motion']
ALL_MOTIONS_QUERY = "select motions.List as Motion from (select distinct motion_shift as 'List', count(*) as 'rcount' from Plays where motion_shift != 'NULL' group by motion_shift order by count(*) desc) motions;"

# format motion_query with "oregon" to get table for specific motion name
MOTION_TABLE_COLS = ['RUN', 'PASS', 'TOTAL']
MOTION_QUERY = "select runs.r as RUN, pass.p as PASS, total.tot as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass UNION ALL select CONCAT(TRUNCATE(runs.r/total.tot*100, 2), '%') as RUN, CONCAT(TRUNCATE(pass.p/total.tot*100, 2), '%') as PASS, '-' as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass;"

# BACKFIELDS

ALL_BACKFIELD_COLS = ['Backfield']
ALL_BACKFIELD_QUERY = "select distinct backfield as Backfield from Plays where  backfield != 'NULL' group by backfield order by count(*) desc;"

# format motion_query with "oregon" to get table for specific motion name
BACKFIELD_TABLE_COLS = ['RUN', 'PASS', 'TOTAL']
BACKFIELD_QUERY = "select runs.r as RUN, pass.p as PASS, total.tot as TOTAL from  (select count(*) as tot from Plays where backfield = {0} and rp != 'n') total, (select count(*) as r from Plays where backfield = {0} and rp = 'r') runs, (select count(*) as p from Plays where backfield = {0} and rp = 'p') pass UNION ALL  select CONCAT(TRUNCATE(runs.r/total.tot*100, 2), '%') as RUN, CONCAT(TRUNCATE(pass.p/total.tot*100, 2), '%') as PASS, '-' as TOTAL from  (select count(*) as tot from Plays where backfield = {0} and rp != 'n') total, (select count(*) as r from Plays where backfield = {0} and rp = 'r') runs, (select count(*) as p from Plays where backfield = {0} and rp = 'p') pass;"


# get downs for 'where down = x and dist <= ...' 

DOWNS_QUERY = "select distinct Plays.genFormation as 'List', count(Plays.down) as 'Count', CONCAT(TRUNCATE((count(Plays.down)/tot.t)*100, 2), '%') as Percent from Plays, (select 'Total', count(*) as 't' from Plays where Plays.genFormation != 'victory' and {0}) tot where Plays.genFormation != 'victory' and {0} group by Plays.genFormation order by count(*) desc;"

TOTALS_QUERY = "select count(*) as 't' from Plays where {0};"

# query to get running and passing drives for each GENFORMATION
	# fill in with: {genFormation}, {R or P}, {down and distance}
GEN_FORMATION = "select distinct Plays.genPlay as 'List', count(*) as 'Count', totals.Total as Num from Plays, (select count(*) as Total from Plays where Plays.genFormation = {0}  and Plays.rp = {1} and {2}) totals where Plays.genFormation = {0} and Plays.rp = {1} and {2} group by Plays.genPlay order by count(*) desc;"

