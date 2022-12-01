/*
SELECT * FROM Availabilities;




SELECT TOP 1 Ca.Username as Caregiver, Av.Time, V.Name, V.Doses
FROM Caregivers as Ca, Availabilities as Av, Vaccines as V
WHERE Ca.Username = Av.Username
AND Av.Time = '2022-11-26'
AND V.Name = 'Weed'
ORDER BY Ca.Username ASC




SELECT V.Doses
FROM Vaccines as V
WHERE V.Name = 'Weed';



INSERT INTO Reserved
VALUES('a20221126BNT', '2022-11-26', 'a', 'nick');


DELETE
FROM Reserved
WHERE Reserved.Appointment_Id ='a20221126';


SELECT COUNT(Name) as count
FROM Vaccines AS VA
WHERE VA.Name = 'BT'



DELETE AV
FROM Reserved AS R, Availabilities as AV
WHERE R.Time = AV.Time
AND AV.Username = R.Caregiver;

SELECT COUNT(Patient)
FROM Reserved AS R
WHERE R.patient = 'nick'


DELETE  from reserved;


INSERT INTO Availabilities
VALUES ('2022-11-26', 'a');
*/

select * from Vaccines