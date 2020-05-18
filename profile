        [Test]
        public async Task TestHealthCHecker()
        {
            var clientFactory = new ClientFactory();
            var sendSettings = new Settings
            {
                GoogleServiceAccountEmail = "gmail-system-test@coral-antonym-256120.iam.gserviceaccount.com",
                GoogleServiceAccountPrivateKey =  "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCnkdhtIyTFU6YE\nnafhxQYPBsyh1Rh6KItM5c4go9jgJQaXmrgk02Myx/jsrZso72A/juO5YfRwtm5N\nG6fu3mpKA8il2he4zw+RA+a3I+V4WeNVrSaRLV3zmoiKYach2tiTb2cto7uQ2lw/\nB+REcUSa4PLpuG3Vu0AMp+arNb3SydfD2/zG1y5o8E3O3ETBsbNZ4X8hE3Jn9dNs\nzpKmqGXdQWUf3GQjqvC+68WE6AXP0KQQY5efd0TrC4xcfdnY2rRQGGjErgW2swTx\nJznBI+9xFgyU9gdVVGqG2Fb2Mz9CG/1F38TvDstvA3SoTdcdX4MFOE/ApgWfHKJz\nTsVl89VlAgMBAAECggEAHNgVCgw/mxvf+vFsYYd5mIKSHNVChlyORelUxveNMGAP\nN29xfR1J+QbFCXCEwdIanjYpatK6seAlMm6tRIfSgfUOx8W3yZ8SzeJ/B01NhZ7r\na+cHOXw2rOUP1coja8dw+kf12bxSYAfGUy83krRwm7xW8/ZEKcM2rjcElLoGd87x\nVQ7OwflA8uxhUJSuOZ8pHAn4TSWs6Ln9lPq2hRNLcZp82yHPjmB3tMoSOojvDBIn\nuIL++BZKMBhKPgjycC8B5tHLEa/N/Ww4JKaa0MGZTguCWMBZmIk6ogTC6ni2HXFv\nQM1zSnv4kA2Q37qhhPSplNYtwhH9sRNQkM4dvUlArQKBgQDWeBkFjV37eYkDiEcV\n95eIHjasYq5RxU5zpco9x+ofIfokfowCMZ8MObwBSgnel4yfHBZkIti1CcsJ/JFY\n2LTlRATqlGZxiqkyO5lWZ1leHZD+pdc/b9sWyJ5Bcl7MScGLWXVflgOq5eSwQ8dX\n0knB3O0CXHZyRfOtyTzDq8AVwwKBgQDIBMwdfWqEsbGU6fj9uGSV3PHeCs2PO2cf\niL2WBsz4N0wZLPOkrnGCmBJ9+zXNmty/hW4MuahhwkmxOnne5r58SiYDUVLRtdkt\n2OprbsAPNmioFPTWFQURIihz+xFGmg0jA7STx3wGGQODtftcVS3jQPG4Ldd8le6H\ngheq6tsttwKBgEd3x+bIwAu/6T+LFx0j35QVdWSmka5gEI+LLMS/rK3pNaEZpnBI\nttZtGtBXKsjJOav/wRpnXk2d0NIoHws7U7SeoQDGqQinC1DY+XUIhYhOU/X3r63N\nCXYjLlFi2mI7JcrY6bsLk3dMmpN+UpxaUAfRJg3GYBYeZ2B/EcemoSDfAoGADypV\n85JzxhXW+gx3ZX1amwZCjGxTQ53kZr6uaTagyd0fdvUyj/TuBFHVbRnj7W/ldtv+\nCRb2jlr1zWs6nEzwemoA0dWTqvTXv6MnuveNtlmQu9XC7oxvcuodGRYbLDg38MSy\nJ1ZDsA6rdowQv+JxdT6SVT2cjgSsLjgN5VajQacCgYBNJXZeGRgtJmVGSPEhEpRI\nUJQPCRE9naRfSMgtQfLQbYStlwj9u5SkPHBlJVBy7COVBF6jgn94eCbKt2ZN7u3J\nnI2kYeiy/CNKv8vf04r5KdhdPhwweCtEqbvK4DpvA38/UWjlWGgE1KRiXjw7y2yJ\nJuHuB7o+rdKZkcm83M61ig==\n-----END PRIVATE KEY-----\n"
            };

            //var readHttpHandler = new HttpHandler(clientFactory);
            //var modifyOath = new GoogleOauthPostBodyFactory(sendSettings);
           //var modifyTokenFactory = new GoogleTokenFactory(readHttpHandler, modifyOath);
           // var modifyTokenFetcher = new GoogleTokenFetcher(modifyTokenFactory, null);
           // var modifyClient = new GmailModifyClient(readHttpHandler, modifyTokenFetcher);


            var prodieUser = "gmailprodie.healthchecker@cccpprodsmoke.com";
            var prodieMessage =
                "TUlNRS1WZXJzaW9uOiAxLjANCkRhdGU6IEZyaSwgNyBGZWIgMjAyMCAxODozNjo0NiArMDAwMA0KTWVzc2FnZS1JRDogPENBTj1rWWRFQ3J4bjJOV1BEMEgxV2tBZDdzdWhXYVo2dHBIaU9YWj1WcGRZRUZlczEwQUBtYWlsLmdtYWlsLmNvbT4NClN1YmplY3Q6IFRlc3QNCkZyb206IEdtYWlsLVByb2RpZSBIZWFsdGhDaGVja2VyIDxnbWFpbHByb2RpZS5oZWFsdGhjaGVja2VyQGNjY3Bwcm9kc21va2UuY29tPg0KVG86IGp1bGl5YS5zbWl0aEBjNDJmYy5jb20NCkNvbnRlbnQtVHlwZTogbXVsdGlwYXJ0L21peGVkOyBib3VuZGFyeT0iMDAwMDAwMDAwMDAwZmYyMTcxMDU5ZTAwYWIwZSINCg0KLS0wMDAwMDAwMDAwMDBmZjIxNzEwNTllMDBhYjBlDQpDb250ZW50LVR5cGU6IG11bHRpcGFydC9hbHRlcm5hdGl2ZTsgYm91bmRhcnk9IjAwMDAwMDAwMDAwMGZmMjE2OTA1OWUwMGFiMGMiDQoNCi0tMDAwMDAwMDAwMDAwZmYyMTY5MDU5ZTAwYWIwYw0KQ29udGVudC1UeXBlOiB0ZXh0L3BsYWluOyBjaGFyc2V0PSJVVEYtOCINCg0KDQoNCi0tMDAwMDAwMDAwMDAwZmYyMTY5MDU5ZTAwYWIwYw0KQ29udGVudC1UeXBlOiB0ZXh0L2h0bWw7IGNoYXJzZXQ9IlVURi04Ig0KDQo8ZGl2IGRpcj0ibHRyIj48YnI-PC9kaXY-DQoNCi0tMDAwMDAwMDAwMDAwZmYyMTY5MDU5ZTAwYWIwYy0tDQotLTAwMDAwMDAwMDAwMGZmMjE3MTA1OWUwMGFiMGUNCkNvbnRlbnQtVHlwZTogdGV4dC9wbGFpbjsgY2hhcnNldD0iVVMtQVNDSUkiOyBuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtRGlzcG9zaXRpb246IGF0dGFjaG1lbnQ7IGZpbGVuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtVHJhbnNmZXItRW5jb2Rpbmc6IGJhc2U2NA0KWC1BdHRhY2htZW50LUlkOiBmX2s2Y2lnc3dzMA0KQ29udGVudC1JRDogPGZfazZjaWdzd3MwPg0KDQpWR1Z6ZEFvSw0KLS0wMDAwMDAwMDAwMDBmZjIxNzEwNTllMDBhYjBlLS0=";

            var prodmtaUser = "gmailprodmta.healthchecker@cccpprodsmoke.com";
            var prodmtaMessage =
                "TUlNRS1WZXJzaW9uOiAxLjANCkRhdGU6IEZyaSwgNyBGZWIgMjAyMCAxODo0MDowNiArMDAwMA0KTWVzc2FnZS1JRDogPENBQ0E4V3g3VFdpbUFEQ1VVeGhxNXAzd3lhT1VxVStZNDJRM3hCTmRmaGVOQWM3dzJNQUBtYWlsLmdtYWlsLmNvbT4NClN1YmplY3Q6IHRlc3QNCkZyb206IEdtYWlsLVByb2RtdGEgSGVhbHRoQ2hlY2tlciA8Z21haWxwcm9kbXRhLmhlYWx0aGNoZWNrZXJAY2NjcHByb2RzbW9rZS5jb20-DQpUbzoganVsaXlhLnNtaXRoQGM0MmZjLmNvbQ0KQ29udGVudC1UeXBlOiBtdWx0aXBhcnQvbWl4ZWQ7IGJvdW5kYXJ5PSIwMDAwMDAwMDAwMDBmNmQzNmUwNTllMDBiNzA1Ig0KDQotLTAwMDAwMDAwMDAwMGY2ZDM2ZTA1OWUwMGI3MDUNCkNvbnRlbnQtVHlwZTogbXVsdGlwYXJ0L2FsdGVybmF0aXZlOyBib3VuZGFyeT0iMDAwMDAwMDAwMDAwZjZkMzZiMDU5ZTAwYjcwMyINCg0KLS0wMDAwMDAwMDAwMDBmNmQzNmIwNTllMDBiNzAzDQpDb250ZW50LVR5cGU6IHRleHQvcGxhaW47IGNoYXJzZXQ9IlVURi04Ig0KDQp0ZXN0DQoNCi0tMDAwMDAwMDAwMDAwZjZkMzZiMDU5ZTAwYjcwMw0KQ29udGVudC1UeXBlOiB0ZXh0L2h0bWw7IGNoYXJzZXQ9IlVURi04Ig0KDQo8ZGl2IGRpcj0ibHRyIj50ZXN0PC9kaXY-DQoNCi0tMDAwMDAwMDAwMDAwZjZkMzZiMDU5ZTAwYjcwMy0tDQotLTAwMDAwMDAwMDAwMGY2ZDM2ZTA1OWUwMGI3MDUNCkNvbnRlbnQtVHlwZTogdGV4dC9wbGFpbjsgY2hhcnNldD0iVVMtQVNDSUkiOyBuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtRGlzcG9zaXRpb246IGF0dGFjaG1lbnQ7IGZpbGVuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtVHJhbnNmZXItRW5jb2Rpbmc6IGJhc2U2NA0KWC1BdHRhY2htZW50LUlkOiBmX2s2Y2lsZ3FxMA0KQ29udGVudC1JRDogPGZfazZjaWxncXEwPg0KDQpWR1Z6ZEFvSw0KLS0wMDAwMDAwMDAwMDBmNmQzNmUwNTllMDBiNzA1LS0=";

            var produs2User = "gmailprodus2.healthchecker@cccpprodsmoke.com";
            var produs2Message =
                "TUlNRS1WZXJzaW9uOiAxLjANCkRhdGU6IEZyaSwgNyBGZWIgMjAyMCAxODozOTozMSArMDAwMA0KTWVzc2FnZS1JRDogPENBR05hNHZLNUcwVGpncUtZLWNvZ1ZkVmFCMml3RUQ5cHNFSC1zd2ctb05fbktkb1U2d0BtYWlsLmdtYWlsLmNvbT4NClN1YmplY3Q6IHRlc3QNCkZyb206IEdtYWlsLVByb2R1czIgSGVhbHRoQ2hlY2tlciA8Z21haWxwcm9kdXMyLmhlYWx0aGNoZWNrZXJAY2NjcHByb2RzbW9rZS5jb20-DQpUbzoganVsaXlhLnNtaXRoQGM0MmZjLmNvbQ0KQ29udGVudC1UeXBlOiBtdWx0aXBhcnQvbWl4ZWQ7IGJvdW5kYXJ5PSIwMDAwMDAwMDAwMDBkZGFiMGYwNTllMDBiNWIxIg0KDQotLTAwMDAwMDAwMDAwMGRkYWIwZjA1OWUwMGI1YjENCkNvbnRlbnQtVHlwZTogbXVsdGlwYXJ0L2FsdGVybmF0aXZlOyBib3VuZGFyeT0iMDAwMDAwMDAwMDAwZGRhYjBkMDU5ZTAwYjVhZiINCg0KLS0wMDAwMDAwMDAwMDBkZGFiMGQwNTllMDBiNWFmDQpDb250ZW50LVR5cGU6IHRleHQvcGxhaW47IGNoYXJzZXQ9IlVURi04Ig0KDQp0ZXN0DQoNCi0tMDAwMDAwMDAwMDAwZGRhYjBkMDU5ZTAwYjVhZg0KQ29udGVudC1UeXBlOiB0ZXh0L2h0bWw7IGNoYXJzZXQ9IlVURi04Ig0KDQo8ZGl2IGRpcj0ibHRyIj50ZXN0PC9kaXY-DQoNCi0tMDAwMDAwMDAwMDAwZGRhYjBkMDU5ZTAwYjVhZi0tDQotLTAwMDAwMDAwMDAwMGRkYWIwZjA1OWUwMGI1YjENCkNvbnRlbnQtVHlwZTogdGV4dC9wbGFpbjsgY2hhcnNldD0iVVMtQVNDSUkiOyBuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtRGlzcG9zaXRpb246IGF0dGFjaG1lbnQ7IGZpbGVuYW1lPSJ0ZXN0LnR4dCINCkNvbnRlbnQtVHJhbnNmZXItRW5jb2Rpbmc6IGJhc2U2NA0KWC1BdHRhY2htZW50LUlkOiBmX2s2Y2lrcTVyMA0KQ29udGVudC1JRDogPGZfazZjaWtxNXIwPg0KDQpWR1Z6ZEFvSw0KLS0wMDAwMDAwMDAwMDBkZGFiMGYwNTllMDBiNWIxLS0=";


            /*var message = new MailMessageFactory(prodieUser, "recipient-a@c42fc.com", "None").CreateMessageWithOneAttachment("Testing", HealthCheckerConstants.HealthCheckerFileName);
            var mimeMessage = MimeMessage.CreateFromMailMessage(message);
            var bytes = Encoding.UTF8.GetBytes(mimeMessage.ToString());
            var rawMessage = WebEncoders.Base64UrlEncode(bytes);*/

            var readSettings = new Settings
            {
                WebhookTopicName = "projects/cccp-191016/topics/prodie-msg-event",
                GoogleServiceAccountEmail = "gmailsvcaccount@cccp-191016.iam.gserviceaccount.com",
                GoogleServiceAccountPrivateKey = "-----BEGIN PRIVATE KEY-----MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCYbtTjUWrgroxsYr8HC6yfn4FGet4FOi4cFGg5nvCXPBymEKKwmMxYDMQBbHzyfOXjn1hmnXAYhnNe6pEEJhaN5quFhzyCSUXAv8KFy4r2bq8k0YjySL4u+yw13rFG8T+pJpBpQ+0lASc8uFXsXCTwIJup1rnJ+ojDSRgiCQ0xAHFjVEo7AKHGT3P7yv/nab6+mAgM1xOVQbfGDz0JXrnvesxzywgdudbLBPEpH6YlXzikECv8L4gTURPWntbbN3nrA27KA/q3Lg0iSsGOe1rEG+RdcNG8Z+itcnDOpqLxGZbAHK4Es70W5FCBqMe+TkcQcmMljAIaB9Ahr7sRJWwPAgMBAAECggEABKwkTzwHVydPpCdroPW0VPBulGqfGg4CFS8UlvfukewwMSrCMSlQDASHEKSnLRiQuK0NC2oBkNnLp5/BgKik81eQhtdU4BSWcXQ4CVxTF6Hf64Aivv/xL7ljtqvrUuxqRow07uowEPEtJzkBpT6CXnBNze78owNcL+z4PrkENv983ca5i5WAW2seDCR/DNPWBntDH0Ag49/mcloO6q5glNcpB7C8EUJyH6EV1KrXBT0frPyZSlQrYg+2Fa4DsdZoWPHo9lHmkgGAyiH7bfU4iy9tu5Qa+u3ip1c/HMueuYglBIpg/5/PIg/nvswe5y9FHK7z5AbL/No0UQ2YqPeO3QKBgQDH+q5g5twqON/amJc6Aer1MW9s88rfRPLsx4YjjN4WJqMa1xwbyoPOvws7HE5r5R1zr+FPl2YvRsti6W3RF+Kf4OP6xfc7Z72J0zCU+s1E5iRUBS7p0olKl/jfMzw8VOSP/hgZxmwCMtjJus3bGrVRC7AcZk6pbADk9Be56mR2TQKBgQDDImnz5rXPACpn/Bz3buztb6Nac6mpX8h7Sr85rffDmSUq8ZFZNqEOoofqpJCrVAIky1KMSuG5RdEko9h+g+J3c9IcoTHlprko4daXPHjUMSOyIyknH3BA+yMw5s3yxn9d8MbQeTD9mKx9eKrlc8Iemd9+9FPHa1wWa8+Fj2KRywKBgQC4jF7gjiwfytzKnobwwVRTcouhwFo4MSj92iOwKw/I4V8kJd+KxhldcnCq3DSC3a2QVX9YNB/ZATwwy7rMe35ojOHXS1odOF9yEbODyPAl5T0hTKc+oUyRyi2hzWaJRs6nE5aqMrL6VHI7uGjBCqTJZj/f9YoiT8mDgL9kkyqjAQKBgQCQFGrzIhh//XlSSj8BG7BpKJMPCHPvkb+v+WL0rdVRYVSmPrO5kbKd4bhFsrj3KBJlJJOQ7wF4EWr5iNkjoTGoTaaIaSU0kkQJQad3B7mXw6i9sWSDdJ0n/cbgJqtOZO5KaKwD5lgcB4zlICHfRffBLJBvZuwtRMI78+LIlTSMvQKBgDLSV/Im8zE9um8mMgXSm9Frl3h44qCFtsfxK03LnyjjtiowQU/urHNc+uHKeKrlCG8+OFoZdu4GXAXzqhGeUB2nP9SS4GGnHUjJrY4igohQcyn9ajqb76PLjadHLqtq4Jw9L99BT79cJaVkrykU+UvwpdlEcczXm/OZNbCl5yJU-----END PRIVATE KEY-----"
            };

            var httpHandler = new HttpHandler(clientFactory);
            var readOath = new GoogleOauthPostBodyFactory(readSettings);
            var readTokenFactory = new GoogleTokenFactory(httpHandler, readOath);
            var readTokenFetcher = new GoogleTokenFetcher(readTokenFactory, null);
            var gmailReader = new GmailReadClient(httpHandler, readTokenFetcher, readSettings);
            await gmailReader.WatchForMessageEvents("gmailprodie.healthchecker@cccpprodsmoke.com");

            readSettings.WebhookTopicName = "projects/cccp-ephemeral/topics/gmail-msg-sent";

            await gmailReader.WatchForMessageEvents("gmailprodie.healthchecker@cccpprodsmoke.com");
            gmailReader = new GmailReadClient(httpHandler, readTokenFetcher, readSettings);
            await gmailReader.WatchForMessageEvents("gmailprodie.healthchecker@cccpprodsmoke.com");

            /*await Task.WhenAll(
                client.SendEmailWithAttachment(prodieUser, prodieMessage),
                client.SendEmailWithAttachment(prodmtaUser, rawMessage),
                client.SendEmailWithAttachment(produs2User, produs2Message));*/
            //var r2 = await client.SendEmailWithAttachment(prodmtaUser, prodmtaMessage);
            //var r3 = await client.SendEmailWithAttachment(produs2User, produs2Message);
            var x = 5;
        }