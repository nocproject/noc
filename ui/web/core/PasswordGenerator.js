//---------------------------------------------------------------------
// NOC.core.PasswordGenerator
// password generator
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.PasswordGenerator");

Ext.define("NOC.core.PasswordGenerator", {
    chrLower: "abcdefghjkmnpqrst",
    chrUpper: "ABCDEFGHJKMNPQRST",
    chrNumbers: "0123456789",
    chrSymbols: "_",

    generate: function(length) {
        var characters = this.chrLower + this.chrUpper + this.chrNumbers + this.chrSymbols,
            randMax = this.chrNumbers.length,
            randMin = randMax - 4,
            index = this.random(0, characters.length - 1),
            password = "";

        for(var i = 0; i < length; i++) {
            var jump = this.random(randMin, randMax);
            index = ((index + jump) > (characters.length - 1) ? this.random(0, characters.length - 1) : index + jump);
            password += characters[index];
        }

        return this.shufflePassword(password);
    },

    random: function(min, max) {
        return Math.floor((Math.random() * max) + min);
    },

    shufflePassword: function(password) {
        return password.split('').sort(function() {
            return 0.5 - Math.random()
        }).join('');
    }
});