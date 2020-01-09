function vendors (theme) {
   return [
        '../../../ui/common/diff_match_patch.js',
        '.pkg_cache/ui/pkg/extjs/ext-all.js',
        `.pkg_cache/ui/pkg/extjs/classic/theme-${theme}/theme-${theme}.js`,
        '.pkg_cache/ui/pkg/extjs/packages/charts/classic/charts.js',
        '.pkg_cache/ui/pkg/jquery/jquery.min.js',
        '.pkg_cache/ui/pkg/codemirror/lib/codemirror.js',
        '.pkg_cache/ui/pkg/codemirror/addon/dialog/dialog.js',
        '.pkg_cache/ui/pkg/codemirror/addon/search/search.js',
        '.pkg_cache/ui/pkg/codemirror/addon/search/searchcursor.js',
        '.pkg_cache/ui/pkg/codemirror/addon/selection/active-line.js',
        '.pkg_cache/ui/pkg/codemirror/addon/mode/loadmode.js',
        '.pkg_cache/ui/pkg/codemirror/addon/edit/matchbrackets.js',
        '.pkg_cache/ui/pkg/codemirror/addon/merge/merge.js',
        '.pkg_cache/ui/pkg/filesaver/filesaver.min.js',
        '.pkg_cache/ui/pkg/visibility/visibility.min.js',
        '.pkg_cache/ui/pkg/moment/moment.min.js',
        '.pkg_cache/ui/pkg/moment-timezone/moment-timezone-with-data-1970-2030.min.js',
    ];
}
module.exports = vendors;
