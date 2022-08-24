require('esbuild').build({
    entryPoints: ['static/js/play.js'],
    bundle: true,
    outdir: 'static/js-build',
}).catch(() => process.exit(1))