import Fluent

struct CreateAcronym: Migration {
    // required by Migration
    // you call when you run your migrations
    func prepare(on database: Database) -> EventLoopFuture<Void> {
        // the table name for this model, this match schema from the model
        database.schema("acronyms")
            .id() // id column in the database
            // columns for short and long
            // column type: string
            // mark columns as required
            .field("short", .string, .required)
            .field("long", .string, .required)
            .field("userID", .uuid, .required, .references("users", "id"))
            .create()
    }
    
    // required by Migration
    // you call when you revert your migrations
    func revert(on database: Database) -> EventLoopFuture<Void> {
        database.schema("acronyms").delete()
    }
}
