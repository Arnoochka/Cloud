@testable import App
import XCTVapor

final class UserTests: XCTestCase {
    let usersName = "Alice"
    let usersUsername = "alicea"
    let usersURI = "/api/users/"
    var app: Application!
    
    override func setUp() async throws {
        app = try await Application.testable()
    }
    
    override func tearDown() async throws {
        app.shutdown()
    }
    
    func testUsersCanBeRetrievedFromAPI() async throws {
        let user = try await User.create(name: usersName, username: usersUsername, on: app.db)
        _ = try await User.create(on: app.db)
        
        try app.test(.GET, usersURI, afterResponse: { response in
            XCTAssertEqual(response.status, .ok)
            let users = try response.content.decode([User].self)
            
            XCTAssertEqual(users.count, 2)
            XCTAssertEqual(users[0].name, usersName)
            XCTAssertEqual(users[0].username, usersUsername)
            XCTAssertEqual(users[0].id, user.id)
        })
    }
    
    func testUserCanBeSavedWithAPI() throws {
        let user = User(name: usersName, username: usersUsername)
        
        try app.test(.POST, usersURI, beforeRequest: { req in
            try req.content.encode(user)
        }, afterResponse: { response in
            let receivedUser = try response.content.decode(User.self)
            XCTAssertEqual(receivedUser.name, usersName)
            XCTAssertEqual(receivedUser.username, usersUsername)
            XCTAssertNotNil(receivedUser.id)
            
            try app.test(.GET, usersURI, afterResponse: { secondResponse in
                let users = try secondResponse.content.decode([User].self)
                XCTAssertEqual(users.count, 1)
                XCTAssertEqual(users[0].name, usersName)
                XCTAssertEqual(users[0].username, usersUsername)
                XCTAssertEqual(users[0].id, receivedUser.id)
            })
        })
    }
    
    func testGettingASingleUserFromTheAPI() async throws {
        let user = try await User.create(
            name: usersName,
            username: usersUsername,
            on: app.db)
        try app.test(.GET, "\(usersURI)\(user.id!)",
                     afterResponse: { response in
            let receivedUser = try response.content.decode(User.self)
            
            XCTAssertEqual(receivedUser.name, usersName)
            XCTAssertEqual(receivedUser.username, usersUsername)
            XCTAssertEqual(receivedUser.id, user.id)
        })
    }
    
    func testGettingAUsersAcronymsFromTheAPI() async throws {
        let user = try await User.create(on: app.db)
        
        let acronymShort = "OMG"
        let acronymLong = "Oh My God"
        
        let acronym1 = try await Acronym.create(
            short: acronymShort,
            long: acronymLong,
            user: user,
            on: app.db)
        _ = try await Acronym.create(
            short: "LOL",
            long: "Laugh Out Loud",
            user: user,
            on: app.db)
        
        try app.test(.GET, "\(usersURI)\(user.id!)/acronyms", afterResponse: { response in
            
            let acronyms = try response.content.decode([Acronym].self)
            
            XCTAssertEqual(acronyms.count, 2)
            XCTAssertEqual(acronyms[0].id, acronym1.id)
            XCTAssertEqual(acronyms[0].long, acronymLong)
            XCTAssertEqual(acronyms[0].short, acronymShort)
        })
    }
    
    /*
    func testUsersCanBeRetrievedFromAPI() async throws {
        let expectedName = "Alice"
        let expectedUsername = "alice"
        
        let app = Application(.testing)
        defer { app.shutdown() }
        try await configure(app)
        try await app.autoRevert().get()
        try await app.autoMigrate().get()
        
        let user = User(name: expectedName, username: expectedUsername)
        try await user.save(on: app.db).get()
        try await User(name: "Luke", username: "lukes")
            .save(on: app.db)
            .get()
        
        try app.test(.GET, "/api/users", afterResponse: { response in
            XCTAssertEqual(response.status, .ok)
            
            let users = try response.content.decode([User].self)
            
            XCTAssertEqual(users.count, 2)
            XCTAssertEqual(users[0].name, expectedName)
            XCTAssertEqual(users[0].username, expectedUsername)
            XCTAssertEqual(users[0].id, user.id)
        })
    }
    */
}
