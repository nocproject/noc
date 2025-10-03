//---------------------------------------------------------------------
// NOC.core.PasswordGenerator
// password generator
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.PasswordGenerator");

Ext.define("NOC.core.PasswordGenerator", {
  chrLower: "abcdefghjkmnpqrstuvwxyz",
  chrUpper: "ABCDEFGHJKMNPQRSTUVWXYZ",
  chrNumbers: "0123456789",
  chrSymbols: "_!@",

  generate: function(length){
    var characters = this.getCharacterSet(),
      password = "";

    password += this.getRandomChar(this.chrLower);
    password += this.getRandomChar(this.chrUpper);
    password += this.getRandomChar(this.chrNumbers);
    password += this.getRandomChar(this.chrSymbols);

    var remainingLength = length - password.length;
    for(var i = 0; i < remainingLength; i++){
      password += this.getRandomChar(characters);
    }

    return this.shufflePassword(password);
  },

  getCharacterSet: function(){
    var chars = this.chrLower + this.chrUpper + this.chrNumbers;
    chars += this.chrSymbols;
    return chars;
  },

  getRandomChar: function(charset){
    var randomIndex = this.cryptoRandom(charset.length);
    return charset[randomIndex];
  },

  cryptoRandom: function(max){
    if(window.crypto && window.crypto.getRandomValues){
      var array = new Uint32Array(1);
      window.crypto.getRandomValues(array);
      return array[0] % max;
    }
    console.warn("Using Math.random() fallback - not cryptographically secure");
    return Math.floor(Math.random() * max);
  },

  shufflePassword: function(password){
    var array = password.split("");
    
    for(var i = array.length - 1; i > 0; i--){
      var j = this.cryptoRandom(i + 1);
      var temp = array[i];
      array[i] = array[j];
      array[j] = temp;
    }
    
    return array.join("");
  },

  checkStrength: function(password){
    var score = 0;
    var checks = {
      length: password.length >= 12,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password), 
      numbers: /[0-9]/.test(password),
      symbols: /[^a-zA-Z0-9]/.test(password),
    };

    Object.keys(checks).forEach(function(key){
      if(checks[key]) score++;
    });

    return {
      score: score,
      strength: score < 3 ? "weak" : score < 4 ? "medium" : "strong",
      checks: checks,
    };
  },
});