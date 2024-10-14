
import * as React from "react"
import { Link, useStaticQuery, graphql } from "gatsby"
import Layout from "@lekoarts/gatsby-theme-minimal-blog/src/components/layout"
import PropTypes from "prop-types"


const Entry = ({ node }) => {
  console.log(node);
  return (
    <div key={node.slug}>
      <Link to={node.slug}><h3>{node.title}</h3></Link>
      <table>
        <tbody>
          <tr>
            <td><b>Author</b>: </td>
            <td>{node.author}</td>
          </tr>
          <tr>
            <td><b>Slug</b>: </td>
            <td><code>{node.slug}</code></td>
          </tr>
          <tr>
            <td><b>Date</b>: </td>
            <td><time>{node.date}</time></td>
          </tr>
        </tbody>
      </table>
      <br></br>
      {/* <p>{node.title}</p> */}
      {/* <p>{node.slug}</p>
      <p>{node.data}</p>
      <p>{node.author}</p> */}
    </div>
  )
}

const CourseProjectList = () => {
  const { allPost } = useStaticQuery(
    graphql`
      query {
        allPost(
          sort: {fields: date, order: DESC}
          filter: {tags: {elemMatch: {name: {eq: "course project"}}}}
        ) {
          nodes {
            slug
            title
            author
            date(formatString:"YYYY-MM-DD")
            excerpt
            timeToRead
            description
            tags {
              name
              slug
            }
          }
        }
      }
    `
  )
  return (
    <Layout>
      <h1>Course Project</h1>
      {allPost.nodes.map((node) => (<Entry node={node} />))}
    </Layout>
  )
}
export default CourseProjectList