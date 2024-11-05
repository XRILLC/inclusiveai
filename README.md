# Class blog

This repository will be used to host your paper summary and a write up of your approaches to the class competition and your course project.

## Getting started


1. Clone this repository.

2. Create and checkout a branch called `<net-id>` (replacing `<net-id>` with your actual NetID):

```bash
# replace <net-id> with your NetID
git checkout -b <net-id>
```

3. Run the following command:

```bash
# set this to either your Net ID or pseudonym
ID=my-id
# create a directory
mkdir -p content/posts/$ID
# copy the structure of /hahnpowell
cp -r content/posts/hahnpowell/ content/posts/$ID/
```

where `ID` should be set to either your NetID or [pseudonym](https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog/_pseudo).

**NOTE: This site will be public, but your identity doesn't have to be.  Per FERPA guidelines, you are not required to reveal your identity publicly in your work for this course.  Instead, you may opt to use the provided [pseudonym generator](https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog/_pseudo).**

4. Commit your changes and push them to the remote:

```bash
git add content/posts/$ID
git commit -m "Initial commit for $ID"
git push -u
```

5. [Open a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)

Your instructor may requests changes.  Make the changes and push them to your remote branch.  Once your pull request is merged, your remote branch will be deleted.  **When you make additional edits (ex. for a subsequent submission), be sure to pull the latest changes from `main` and create a new branch**.

## Tasks

You'll be editing at least three files (each is associated with a different assignment):

- `content/posts/<my-id>/paper-summary/index.mdx`
  - your summary of an NLP paper

- `content/posts/<my-id>/course-project/index.mdx`
  - your summary of your course project and results

- `content/posts/<my-id>/class-competition/index.mdx`
  - your summary of your approach to and results for the class-wide competition [hosted on kaggle](https://www.kaggle.com/c/ling-582-fa-2024-course-competition) (**note: in order to view that page, you'll first need to accept the competition invite through D2L**)

### 1. Paper summary

See https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog/assignments/paper-summary for details

Alter `content/posts/<my-id>/paper-summary/index.mdx`:

```markdown
---
title: "Title of Paper"
slug: "/<my-id>/paper-summary"
author: "<my-id>"
date: YYYY-MM-DD
```

- Replace `<my-id>` in the example above with your ID.

- Replace `YYYY-MM-DD` with the date of your post ("October 31 2024" -> `2024-10-31`).

Your post should be written in a superset of markdown ([MDX](https://mdxjs.com/)). You're free to mix in HTML, javascript, etc. as needed.

### 2. Class-wide competition (kaggle)

See https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog/assignments/class-competition for details

Alter `content/posts/<my-id>/class-competition/index.mdx`:

```markdown
---
title: "Clever title summarizing approach"
slug: "/<my-id>/class-competition"
author: "<my-id>"
date: YYYY-MM-DD
```

- Replace `<my-id>` in the example above with your ID.

- Replace `YYYY-MM-DD` with the date of your post ("October 31 2024" -> `2024-10-31`).

Your post should be written in a superset of markdown ([MDX](https://mdxjs.com/)). You're free to mix in HTML, javascript, etc. as needed.

### 3. Course project (your pick)

See https://uazhlt-ms-program.github.io/ling-582-fall-2024-course-blog/assignments/course-project for details

Alter `content/posts/<my-id>/course-project/index.mdx`:
 
```markdown
---
title: "Clever title summarizing project"
slug: "/<my-id>/course-project"
author: "<my-id>"
date: YYYY-MM-DD
```

- Replace `<my-id>` in the example above with your ID.

- Replace `YYYY-MM-DD` with the date of your post ("October 31 2024" -> `2024-10-31`).

Your post should be written in a superset of markdown ([MDX](https://mdxjs.com/)). You're free to mix in HTML, javascript, etc. as needed.

# Workflow

You will commit all of your changes on a branch `<net-id>` where `<net-id>` represents your Net ID. On your branch, create a directory under `content/posts/<my-id>` that mirrors the example at `content/posts/hahnpowell`.  Once you've completed your post, [open a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

# Develop

The site should be developed using `docker`.

**Commits that end up in `main` trigger an automated deployment to the `gh-pages` branch.**

## Docker-based method

Pull the docker image:

```bash
docker pull "uazhlt/ling-582-course-blog:latest"
```

Launch the site in development mode on port 8881:

```bash
docker run -it -p "8881:8000" -v "$PWD:/app" "uazhlt/ling-582-course-blog:latest"
```

Open your browser to `localhost:8881` for a live preview of the site.

# Handling merge conflicts

If you do not keep your branch up-to-date with changes to the default branch (`main`), eventually you will run into **merge conflicts**.

## Resolving merge conflicts

1. check out the `main` branch (`git checkout main`)
2. pull changes to `main` from the remote (`git pull origin main`)
3. checkout your branch again (`git checkout mybranchnamehere`)
4. merge `main` into your branch (`git merge main`).  
5. correct the conflicts in your code editor of choice
6. commit your changes (`git commit -m "resolved merge conflict"`)
7. push to your remote branch

More information on this process can be found here:

- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github

# MDX

For a demonstration of some commonly used MDX features `content/pages/example`, As the `slug` field in the frontmatter for `content/pages/example/index.mdx` suggests, this page is accessible at `/example` when running the site locally.
