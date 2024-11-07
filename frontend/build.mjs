import esbuild from "esbuild"
import glob from "tiny-glob"

const isDev = process.argv.includes("-d");
const isProd = process.argv.includes("-p")

// Note that this is not "watched", new files will not be built unless node is restarted
// Also note that we only include top level files
// Also note, the path is from where the script is called, not the location of this file
let entryPoints = await glob("./frontend/static/js/pages/**/*.js");

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
        outdir: './frontend/static/js-build',
        define: (isProd 
            ? {'process.env.LIVE_WS_SERVER': '"wss://live.wikispeedruns.com"'}
            : {}
        ),
    })
} catch(err) {
    process.exit(1)
}
