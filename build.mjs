import esbuild from "esbuild"
import glob from "tiny-glob"

const isDev = process.argv.includes("-d");

// Note that this is not "watched", new files will not be built unless node is restarted
// Also note that we only include top level files
let entryPoints = await glob("./static/js/pages/**/*.js");
console.log("Building the following files:")
console.log(entryPoints);


try{
    esbuild.build({
        entryPoints: entryPoints,
        bundle: true,
        minify: !isDev,
        sourcemap: isDev,
        watch: isDev,
        logLevel: "info",
        outdir: 'static/js-build',
    })
} catch(err) {
    process.exit(1)
}
