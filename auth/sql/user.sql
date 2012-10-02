DROP TABLE jtax_propertytax;


CREATE TABLE jtax_challengepropertytaxitem (
id int4 DEFAULT nextval('jtax_challengepropertytaxitem_id_seq'::regclass) NOT NULL,
propertytaxitemid_id int4 NOT NULL,
citizenid int4 NOT NULL,
staffid int4 NOT NULL,
challengestartdate timestamptz(6) NOT NULL,
challengeenddate timestamptz(6) NOT NULL
)
WITH (OIDS=FALSE)

;

CREATE TABLE jtax_challengepropertytaxitemmedia (
id int4 DEFAULT nextval('jtax_challengepropertytaxitemmedia_id_seq'::regclass) NOT NULL,
challengepropertytaxitemid_id int4 NOT NULL,
mediatype varchar(4) NOT NULL,
mediafile varchar(100) NOT NULL,
staffid int4 NOT NULL,
mediadatetime timestamptz(6) NOT NULL
)
WITH (OIDS=FALSE)

;

CREATE TABLE jtax_challengepropertytaxitemnote (
id int4 DEFAULT nextval('jtax_challengepropertytaxitemnote_id_seq'::regclass) NOT NULL,
challengepropertytaxitemid_id int4 NOT NULL,
staffid int4 NOT NULL,
note text NOT NULL
)
WITH (OIDS=FALSE)

;

CREATE TABLE jtax_paypropertytaxitem (
id int4 DEFAULT nextval('jtax_paypropertytaxitem_id_seq'::regclass) NOT NULL,
propertytaxitemid_id int4 NOT NULL,
citizenid int4 NOT NULL,
staffid int4 NOT NULL,
paydate timestamptz(6) NOT NULL,
note varchar(255) NOT NULL
)
WITH (OIDS=FALSE)

;

CREATE TABLE jtax_propertytaxitem (
id int4 DEFAULT nextval('jtax_propertytaxitem_id_seq'::regclass) NOT NULL,
plotid int4 NOT NULL,
amount numeric(20,2) NOT NULL,
currency varchar(4) NOT NULL,
startdate timestamptz(6) NOT NULL,
enddate timestamptz(6) NOT NULL,
dategenerated timestamptz(6) NOT NULL,
ispaid bool NOT NULL,
ischanllenged bool NOT NULL,
isreviewed bool NOT NULL,
isaccepted bool NOT NULL,
staffid int4 NOT NULL
)
WITH (OIDS=FALSE)

;

CREATE TABLE jtax_reviewpropertytaxitem (
id int4 DEFAULT nextval('jtax_reviewpropertytaxitem_id_seq'::regclass) NOT NULL,
challengepropertytaxitemid_id int4 NOT NULL,
staffid int4 NOT NULL,
reviewdate timestamptz(6) NOT NULL,
note varchar(255) NOT NULL
)
WITH (OIDS=FALSE)

;