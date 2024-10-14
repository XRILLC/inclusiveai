require(`dotenv`).config({
  path: `.env`,
})
const remarkMath = require(`remark-math`)
const rehypeKatex = require(`rehype-katex`)

const shouldAnalyseBundle = process.env.ANALYSE_BUNDLE
const courseName = `LING 582`
const courseRun = `FA 2024`
module.exports = {
  pathPrefix: `/ling-582-fall-2024-course-blog`,
  siteMetadata: {
    // see https://github.com/LekoArts/gatsby-themes/tree/master/themes/gatsby-theme-minimal-blog
    // Used for the title template on pages other than the index site
    siteTitle: `LING 582 (FA 2024)`,
    // Default title of the page
    siteTitleAlt: `LING 582 (FA 2024)`,
    // Can be used for e.g. JSONLD
    siteHeadline: `Course blog`,
    // Will be used to generate absolute URLs for og:image etc.
    siteUrl: `https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog`,
    // Used for SEO
    siteDescription: `This is the homepage for the ${courseName} (${courseRun}) course blog.`,
    // Will be set on the <html /> tag
    siteLanguage: `en`,
    // Used for og:image and must be placed inside the `static` folder
    siteImage: `/example.jpg`,
    author: `@myedibleenso`
  },
  plugins: [
    {
      resolve: `gatsby-plugin-typescript`,
      options: {
        isTSX: true, // defaults to false
        jsxPragma: `jsx`, // defaults to "React"
        allExtensions: true, // defaults to false
      },
    },
    {
      resolve: `@lekoarts/gatsby-theme-minimal-blog`,
      // See the theme's README for all available options
      options: {
        //mdx: false,
        formatString: `MM/DD/YYYY`,
        navigation: [
          // {
          //   title: `Blog`,
          //   slug: `/blog`,
          // },
          {
            title: `About`,
            slug: `/`,
          },
          {
            title: `Assignments`,
            slug: `/assignments`,
          },
          {
            title: `Posts`,
            slug: `/student-posts`,
          },
          // {
          //   title: `Docs`,
          //   slug: `/docs`,
          // },
        ],
        externalLinks: [
          {
            name: `GitHub`,
            url: `https://github.com/uazhlt-ms-program/ling-582-fall-2024-course-blog`,
          }
          // {
          //   name: `Twitter`,
          //   url: `https://twitter.com/myedibleenso`,
          // },
        ],
      },
    },
    {
      resolve: `gatsby-omni-font-loader`,
      options: {
        enableListener: true,
        preconnect: [`https://fonts.gstatic.com`],
        interval: 300,
        timeout: 30000,
        // If you plan on changing the font you'll also need to adjust the Theme UI config to edit the CSS
        // See: https://github.com/LekoArts/gatsby-themes/tree/main/examples/minimal-blog#changing-your-fonts
        web: [
          {
            name: `IBM Plex Sans`,
            file: `https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap`,
          },
        ],
      },
    },
    {
      resolve: `gatsby-plugin-mdx`,
      options: {
        extensions: [`.mdx`, `.md`],
        remarkPlugins: [remarkMath],
        gatsbyRemarkPlugins: [
          {
            resolve: `gatsby-remark-images`,
            options: {
              maxWidth: 960,
              quality: 90,
              linkImagesToOriginal: false,
            },
          },
          {
            resolve: `gatsby-remark-katex`,
            options: {
              // Add any KaTeX options from https://github.com/KaTeX/KaTeX/blob/master/docs/options.md here
              strict: `ignore`
            }
          },
          {
            resolve: "gatsby-remark-embed-video",
            options: {
              width: 800,
              ratio: 1.77, // Optional: Defaults to 16/9 = 1.77
              height: 400, // Optional: Overrides optional.ratio
              related: false, //Optional: Will remove related videos from the end of an embedded YouTube video.
              noIframeBorder: true, //Optional: Disable insertion of <style> border: 0
              urlOverrides: [
                {
                  id: 'youtube',
                  embedURL: (videoId) => `https://www.youtube-nocookie.com/embed/${videoId}`,
                }
              ], //Optional: Override URL of a service provider, e.g to enable youtube-nocookie support
              containerClass: 'embedVideo-container', //Optional: Custom CSS class for iframe container, for multiple classes separate them by space
            }
          },
          {
            resolve: `gatsby-remark-autolink-headers`,
            options: {
              offsetY: `100`,
              icon: `<svg aria-hidden="true" height="20" version="1.1" viewBox="0 0 16 16" width="20"><path fill-rule="evenodd" d="M4 9h1v1H4c-1.5 0-3-1.69-3-3.5S2.55 3 4 3h4c1.45 0 3 1.69 3 3.5 0 1.41-.91 2.72-2 3.25V8.59c.58-.45 1-1.27 1-2.09C10 5.22 8.98 4 8 4H4c-.98 0-2 1.22-2 2.5S3 9 4 9zm9-3h-1v1h1c1 0 2 1.22 2 2.5S13.98 12 13 12H9c-.98 0-2-1.22-2-2.5 0-.83.42-1.64 1-2.09V6.25c-1.09.53-2 1.84-2 3.25C6 11.31 7.55 13 9 13h4c1.45 0 3-1.69 3-3.5S14.5 6 13 6z"></path></svg>`,
              className: `md-header`,
              maintainCase: false,
              removeAccents: true,
            },
          },      
          // see https://github.com/ptigas/gatsby-remark-bibliography
          {
            resolve: `gatsby-remark-bibliography`
          }
        ],
        plugins: [
          {
            resolve: `gatsby-remark-images`,
            options: {
              maxWidth: 960,
              quality: 90,
              linkImagesToOriginal: false,
            },
          },
          {
            resolve: `gatsby-remark-bibliography`
          }
        ],
      },
    },
    `gatsby-plugin-sitemap`,
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `LING 582 (SP 2024 course blog)`,
        short_name: `pan-dl`,
        description: `LING 582 (SP 2024 course blog)`,
        start_url: `/`,
        background_color: `#fff`,
        theme_color: `#6B46C1`,
        display: `standalone`,
        icons: [
          {
            src: `/android-chrome-192x192.png`,
            sizes: `192x192`,
            type: `image/png`,
          },
          {
            src: `/android-chrome-512x512.png`,
            sizes: `512x512`,
            type: `image/png`,
          },
        ],
      },
    },
    {
      resolve: `gatsby-alias-imports`,
      options: {
        aliases: {
          "@src": `src`,
        }
      }
    },
    {
      resolve: `gatsby-plugin-feed`,
      options: {
        query: `
          {
            site {
              siteMetadata {
                title: siteTitle
                description: siteDescription
                siteUrl
                site_url: siteUrl
              }
            }
          }
        `,
        feeds: [
          {
            serialize: ({ query: { site, allPost } }) =>
              allPost.nodes.map((post) => {
                const url = site.siteMetadata.siteUrl + post.slug
                const content = `<p>${post.excerpt}</p><div style="margin-top: 50px; font-style: italic;"><strong><a href="${url}">Keep reading</a>.</strong></div><br /> <br />`

                return {
                  title: post.title,
                  date: post.date,
                  author: post.author,
                  excerpt: post.excerpt,
                  url,
                  guid: url,
                  custom_elements: [{ "content:encoded": content }],
                }
              }),
            query: `
              {
                allPost(sort: { fields: date, order: DESC }) {
                  nodes {
                    title
                    date(formatString: "MMMM D, YYYY")
                    author
                    excerpt
                    slug
                  }
                }
              }
            `,
            output: `rss.xml`,
            title: `${courseName} (${courseRun}) course blog`,
          },
        ],
      },
    },
    `gatsby-plugin-remove-serviceworker`,
    shouldAnalyseBundle && {
      resolve: `gatsby-plugin-webpack-bundle-analyser-v2`,
      options: {
        analyzerMode: `static`,
        reportFilename: `_bundle.html`,
        openAnalyzer: false,
      },
    },
  ].filter(Boolean),
}
