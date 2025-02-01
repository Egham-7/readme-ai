/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file was automatically generated by TanStack Router.
// You should NOT make any changes in this file as it will be overwritten.
// Additionally, you should also exclude this file from your linter and/or formatter to prevent it from being checked or modified.

// Import Routes

import { Route as rootRoute } from "./routes/__root"
import { Route as HomeImport } from "./routes/_home"
import { Route as IndexImport } from "./routes/index"
import { Route as HomeHomeImport } from "./routes/_home/home"

// Create/Update Routes

const HomeRoute = HomeImport.update({
  id: "/_home",
  getParentRoute: () => rootRoute,
} as any)

const IndexRoute = IndexImport.update({
  id: "/",
  path: "/",
  getParentRoute: () => rootRoute,
} as any)

const HomeHomeRoute = HomeHomeImport.update({
  id: "/home",
  path: "/home",
  getParentRoute: () => HomeRoute,
} as any)

// Populate the FileRoutesByPath interface

declare module "@tanstack/react-router" {
  interface FileRoutesByPath {
    "/": {
      id: "/"
      path: "/"
      fullPath: "/"
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    "/_home": {
      id: "/_home"
      path: ""
      fullPath: ""
      preLoaderRoute: typeof HomeImport
      parentRoute: typeof rootRoute
    }
    "/_home/home": {
      id: "/_home/home"
      path: "/home"
      fullPath: "/home"
      preLoaderRoute: typeof HomeHomeImport
      parentRoute: typeof HomeImport
    }
  }
}

// Create and export the route tree

interface HomeRouteChildren {
  HomeHomeRoute: typeof HomeHomeRoute
}

const HomeRouteChildren: HomeRouteChildren = {
  HomeHomeRoute: HomeHomeRoute,
}

const HomeRouteWithChildren = HomeRoute._addFileChildren(HomeRouteChildren)

export interface FileRoutesByFullPath {
  "/": typeof IndexRoute
  "": typeof HomeRouteWithChildren
  "/home": typeof HomeHomeRoute
}

export interface FileRoutesByTo {
  "/": typeof IndexRoute
  "": typeof HomeRouteWithChildren
  "/home": typeof HomeHomeRoute
}

export interface FileRoutesById {
  __root__: typeof rootRoute
  "/": typeof IndexRoute
  "/_home": typeof HomeRouteWithChildren
  "/_home/home": typeof HomeHomeRoute
}

export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths: "/" | "" | "/home"
  fileRoutesByTo: FileRoutesByTo
  to: "/" | "" | "/home"
  id: "__root__" | "/" | "/_home" | "/_home/home"
  fileRoutesById: FileRoutesById
}

export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  HomeRoute: typeof HomeRouteWithChildren
}

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  HomeRoute: HomeRouteWithChildren,
}

export const routeTree = rootRoute
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/_home"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/_home": {
      "filePath": "_home.tsx",
      "children": [
        "/_home/home"
      ]
    },
    "/_home/home": {
      "filePath": "_home/home.tsx",
      "parent": "/_home"
    }
  }
}
ROUTE_MANIFEST_END */
