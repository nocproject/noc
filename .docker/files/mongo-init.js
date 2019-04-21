db = db.getSiblingDB('noc');
db.createUser({
    user: "noc" ,
    pwd: "noc",
    roles: [
        { role:"dbOwner", db: "noc" }
    ]
});
db = db.getSiblingDB('noc_tests');
db.createUser({
    user: "noc" ,
    pwd: "noc",
    roles: [
        { role:"dbOwner", db: "noc_tests" }
    ]
});
