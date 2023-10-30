import Vapor
import Fluent

final class Acronym: Model {
    // specify the schema as required by Model.
    // this is the name of the table in the database
    static let schema = "acronyms"
    
    // an optional id property that stores the ID of the model
    // if one has been set.
    // the Fluent wrapper tells Fluent 
    // what to use to look up the model in the database
    @ID
    var id: UUID?
    
    // two string properties to hold the acronym and its definition.
    // the Fluent wrapper uses to denote a generic database field.
    // the key paramete is the name of the column in the database
    @Field(key: "short")
    var short: String
    
    @Field(key: "long")
    var long: String
    
    @Parent(key: "userID")
    var user: User
    
    @Siblings(through: AcronymCategoryPivot.self, from: \.$acronym, to: \.$category)
    var categories: [Category]
    
    // Fluent uses this to initialize models
    // returned from database quiries
    init() {}
    
    // initializer to create the model as required
    init(id: UUID? = nil, short: String, long: String, userID: User.IDValue) {
        self.id = id
        self.short = short
        self.long = long
        self.$user.id = userID
    }
}

extension Acronym: Content {}
