if (! this.sh_languages) {
  this.sh_languages = {};
}
sh_languages['bind'] = [
  [
    [
      /;/g,
      'sh_comment',
      1
    ],
    [
      /\b[+-]?(?:(?:0x[A-Fa-f0-9]+)|(?:(?:[\d]*\.)?[\d]+(?:[eE][+-]?[\d]+)?))u?(?:(?:int(?:8|16|32|64))|L)?\b/g,
      'sh_number',
      -1
    ],
    [
      /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:\/[0-9]{1,2})?/g,
      'sh_address',
      -1
    ],
    [
      /@|IN|SOA|A|NS|CNAME|MX|PTR|SRV/g,
      'sh_keyword',
      -1
    ],
    [
      /^[ \t]*(?:\$.*)/g,
      'sh_preproc',
      -1
    ]
  ],
  [
    [
      /$/g,
      null,
      -2
    ]
  ]
];
