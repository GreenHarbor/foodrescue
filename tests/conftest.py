import pytest


@pytest.fixture
def client():
    from src import app

    app.app.config['TESTING'] = True

    with app.app.app_context():

        with app.db.engine.begin() as connection:
            from sqlalchemy import text
            connection.execute(text('DROP TABLE IF EXISTS `foodrescue`;'))

            connection.execute(text('''CREATE TABLE `foodrescue` (
  `post_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) NOT NULL,
  `description` varchar(256) NOT NULL,
  `dateposted` datetime(6) NOT NULL,
  `datefrom` datetime(6) NOT NULL,
  `dateto` datetime(6) NOT NULL,
  `coordinate_long` varchar(64) NOT NULL,
  `coordinate_lat` varchar(64) NOT NULL,
  `location` varchar(64) NOT NULL,
  `foodtype` varchar(64) NOT NULL,
  `verified` BOOL NOT NULL,
  PRIMARY KEY (`post_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28;
'''))

            connection.execute(text('''INSERT INTO `foodrescue`
VALUES (1, 'Chicken Satay',
'Skewered, grilled chicken marinated in aromatic spices',
'2023-09-18 12:00:00', '2023-09-18 14:00:00',
'2023-09-18 18:00:00', '21.67890', '91.54789',
'80 Stamford Rd, Singapore 178902', 'Normal', TRUE),
(2, 'Vegetarian Pasta',
'Leftover baked ziti with marinara sauce and vegetables. Can be reheated.',
'2023-09-19 15:00:00', '2023-09-19 16:00:00',
'2023-09-19 18:00:00', '1.290210', '103.755760',
'50 Jurong Gateway Rd, Singapore 608549', 'Vegetarian', TRUE)'''))

    return app.app.test_client()
