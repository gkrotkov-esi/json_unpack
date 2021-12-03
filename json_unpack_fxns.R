#json_unpack_fxns
# Gabriel Krotkov
# 12/1/2021

load_libraries <- function(){
  library(rjson)
  library(tidyverse)
}

load_data <- function(filepath){
  data <- rjson::fromJSON(sprintf("[%s]", 
                                  paste(readLines(filepath),collapse=",")))
  return(data)
}

# returns the ticketID of one json object
get_id <- function(item){
  return(item$id)
}

# returns the ticketID of all json objects
get_ids <- function(data){
  return(unlist(lapply(data, get_id), recursive = FALSE))
}

# returns a vector of the comments in one json object
get_item_comments <- function(item){
  return(item$comments)
}

# gets only the comment body of the item
# designed to work with get_data_comments fxn
get_item_comment_body <- function(item){
  return(item$comments[[1]]$body)
}

# returns a list of all the comments in all the json objects
get_data_comments <- function(data){
  result <- vector(mode = "list", length = length(data))
  for (i in 1:length(data)){
    # we suppress warnings since we're intentionally making a ragged list
    # (ragged meaning nonrectangular)
    suppressWarnings(result[i] <- get_item_comment_body(data[[i]]))
  }
  return(result)
}

construct_data_frame <- function(data){
  ids <- get_ids(data)
  comments <- get_data_comments(data)
  result <- data.frame(id = ids)
  result$comments <- comments
  return(result)
}


# @TODO only include comment body in comment column
# access token: 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

# making some example changes