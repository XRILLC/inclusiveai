// see https://github.com/LekoArts/gatsby-themes/issues/438#issuecomment-653674876

const addFrontmatterField = (name) => async (source, args, context) => {
  const mdxNode = context.nodeModel.getNodeById({
    id: source.parent,
  })
  return mdxNode.frontmatter[name]
}

exports.createSchemaCustomization = ({ actions }) => {
  const { createTypes, createFieldExtension } = actions

  createFieldExtension({
    name: `addFrontmatterField`,
    args: {
      name: `String!`,
    },
    extend({ name }) {
      return {
        resolve: addFrontmatterField(name),
      }
    },
  })

  createTypes(`
    interface Post @nodeInterface {
      author: String
    }
    
    type MdxPost implements Node & Post {
      author: String @addFrontmatterField(name: "author")
    }
  `)
}